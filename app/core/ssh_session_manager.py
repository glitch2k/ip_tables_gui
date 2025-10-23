"""
Module: ssh_session_manager
Phase: 3
Milestone: 3
Step: 3
Purpose:
    Persistent SSH session manager with resilience:
      - Session cache per (host,user,port)
      - Auto-retry with exponential backoff on transient failures
      - Idle TTL sweeper thread
      - Per-host metrics (successes, failures, retries, last_latency, last_error)
      - Optional TCP keepalive to avoid idle drops
"""

from __future__ import annotations
import time
import threading
from typing import Dict, Tuple, Optional

import paramiko
import socket


# ---------- Tunables ----------
DEFAULT_TIMEOUT_S      = 5          # connect/read timeout
IDLE_TTL_S             = 300        # close sessions idle > 5 minutes
HOUSEKEEP_FREQ_S       = 30         # sweep cache every 30s
RETRY_ATTEMPTS         = 2          # number of *additional* attempts after the first try
RETRY_INITIAL_DELAY_S  = 0.5        # backoff base
RETRY_BACKOFF_FACTOR   = 2.0        # exponential backoff
TCP_KEEPALIVE          = True       # enables TCP keepalive on the transport
TCP_KEEPALIVE_IDLE_S   = 30
TCP_KEEPALIVE_INTL_S   = 15
TCP_KEEPALIVE_CNT      = 4


class _ManagedSession:
    """Holds a live Paramiko SSHClient plus last-used timestamp."""
    def __init__(self, client: paramiko.SSHClient):
        self.client = client
        self.last_used = time.time()

    def touch(self):
        self.last_used = time.time()


class SSHSessionManager:
    """
    Thread-safe pool of SSH sessions with resilience.
    - get_session(): connect/reuse session
    - exec(): run command with auto-retry/backoff
    - metrics(): per-host counters & last error/latency
    """
    def __init__(self, idle_ttl_s: int = IDLE_TTL_S):
        self._cache: Dict[Tuple[str, str, int], _ManagedSession] = {}
        self._lock = threading.RLock()
        self._idle_ttl_s = idle_ttl_s
        self._metrics: Dict[Tuple[str, str, int], Dict[str, float | int | str | None]] = {}
        self._sweeper = _Sweeper(self, HOUSEKEEP_FREQ_S)
        self._sweeper.start()

    # ---------- Connection ----------
    def _connect(
        self,
        host: str,
        user: str,
        key_path: str,
        port: int = 22,
        timeout: int = DEFAULT_TIMEOUT_S,
    ) -> paramiko.SSHClient:
        key = paramiko.RSAKey.from_private_key_file(key_path)
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=host, username=user, pkey=key, port=port, timeout=timeout)

        # Optional TCP keepalive tweaks to reduce idle disconnects
        try:
            if TCP_KEEPALIVE:
                transport = client.get_transport()
                if transport is not None:
                    sock = transport.sock
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                    # platform-specific options; ignore if not available
                    if hasattr(socket, "TCP_KEEPIDLE"):
                        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, TCP_KEEPALIVE_IDLE_S)
                    if hasattr(socket, "TCP_KEEPINTVL"):
                        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, TCP_KEEPALIVE_INTL_S)
                    if hasattr(socket, "TCP_KEEPCNT"):
                        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, TCP_KEEPALIVE_CNT)
        except Exception:
            # Keep manager resilient; keepalive is a best-effort optimization
            pass

        return client

    def get_session(
        self,
        host: str,
        user: str,
        key_path: str,
        port: int = 22,
        timeout: int = DEFAULT_TIMEOUT_S,
    ) -> paramiko.SSHClient:
        k = (host, user, port)
        with self._lock:
            ms = self._cache.get(k)
            if ms and self._is_alive(ms.client):
                ms.touch()
                return ms.client

            # (re)connect
            client = self._connect(host, user, key_path, port, timeout)
            self._cache[k] = _ManagedSession(client)
            self._ensure_metrics(k)
            return client

    # ---------- Exec with retry/backoff ----------
    def exec(
        self,
        host: str,
        user: str,
        key_path: str,
        command: str,
        port: int = 22,
        timeout: int = DEFAULT_TIMEOUT_S,
    ) -> dict:
        """
        Returns dict(status, exit_code, stdout, stderr, message, retries, latency_ms, error_type?)
        Retries a failed attempt up to RETRY_ATTEMPTS with exponential backoff.
        """
        k = (host, user, port)
        self._ensure_metrics(k)

        attempt = 0
        delay = RETRY_INITIAL_DELAY_S
        start_total = time.perf_counter()
        last_error_type = None
        last_exc = None

        while True:
            attempt += 1
            t0 = time.perf_counter()
            try:
                client = self.get_session(host, user, key_path, port, timeout)
                result = self._exec_with_client(client, command)
                latency_ms = int((time.perf_counter() - t0) * 1000)

                # success path
                if result["status"] == "success":
                    result["retries"] = attempt - 1
                    result["latency_ms"] = latency_ms
                    self._bump_metric(k, "successes", 1)
                    self._set_metric(k, "last_latency_ms", latency_ms)
                    self._set_metric(k, "last_error", None)
                    return result

                # SSHChannelError/SocketError handled as transient
                if result.get("error_type") in ("SSHChannelError", "SocketError"):
                    last_error_type = result["error_type"]
                    last_exc = result["stderr"]
                    self.close_host(host, user, port)  # force reconnect next try
                    if attempt <= (1 + RETRY_ATTEMPTS):
                        self._bump_metric(k, "retries", 1)
                        time.sleep(delay)
                        delay *= RETRY_BACKOFF_FACTOR
                        continue

                # non-transient failure (exit_code != 0, or other)
                self._bump_metric(k, "failures", 1)
                self._set_metric(k, "last_latency_ms", latency_ms)
                self._set_metric(k, "last_error", result.get("stderr") or result.get("message"))
                result["retries"] = attempt - 1
                result["latency_ms"] = latency_ms
                return result

            except paramiko.AuthenticationException as e:
                last_error_type = "AuthenticationError"
                last_exc = str(e)
                self._bump_metric(k, "failures", 1)
                return _err("AuthenticationError", f"Auth failed for {user}@{host}", e, retries=attempt-1)

            except (paramiko.SSHException, socket.error) as e:
                last_error_type = "SSHError"
                last_exc = str(e)
                self.close_host(host, user, port)
                if attempt <= (1 + RETRY_ATTEMPTS):
                    self._bump_metric(k, "retries", 1)
                    time.sleep(delay)
                    delay *= RETRY_BACKOFF_FACTOR
                    continue
                self._bump_metric(k, "failures", 1)
                return _err("SSHError", f"SSH error on {host}", e, retries=attempt-1)

            except Exception as e:
                last_error_type = "GeneralError"
                last_exc = str(e)
                self._bump_metric(k, "failures", 1)
                return _err("GeneralError", f"Unexpected error for {host}", e, retries=attempt-1)

            finally:
                total_ms = int((time.perf_counter() - start_total) * 1000)
                self._set_metric(k, "last_total_ms", total_ms)
                if last_error_type:
                    self._set_metric(k, "last_error_type", last_error_type)
                    self._set_metric(k, "last_error", last_exc)

    def _exec_with_client(self, client: paramiko.SSHClient, command: str) -> dict:
        try:
            stdin, stdout, stderr = client.exec_command(command)
            exit_code = stdout.channel.recv_exit_status()
            return {
                "status": "success" if exit_code == 0 else "failure",
                "exit_code": exit_code,
                "stdout": stdout.read().decode().strip(),
                "stderr": stderr.read().decode().strip(),
                "message": f"Executed '{command}' (exit {exit_code})",
            }
        except socket.error as e:
            return _err("SocketError", "Socket error while executing command", e)
        except paramiko.SSHException as e:
            return _err("SSHChannelError", "SSH channel error while executing command", e)

    # ---------- Health ----------
    def _is_alive(self, client: paramiko.SSHClient) -> bool:
        try:
            transport = client.get_transport()
            return bool(transport and transport.is_active())
        except Exception:
            return False

    # ---------- Metrics ----------
    def _ensure_metrics(self, key: Tuple[str, str, int]):
        if key not in self._metrics:
            self._metrics[key] = {
                "successes": 0,
                "failures": 0,
                "retries":  0,
                "last_latency_ms": None,
                "last_total_ms": None,
                "last_error_type": None,
                "last_error": None,
            }

    def _bump_metric(self, key: Tuple[str, str, int], field: str, inc: int):
        self._ensure_metrics(key)
        self._metrics[key][field] = int(self._metrics[key][field]) + inc

    def _set_metric(self, key: Tuple[str, str, int], field: str, value):
        self._ensure_metrics(key)
        self._metrics[key][field] = value

    def metrics(self) -> Dict[Tuple[str, str, int], Dict[str, int | float | str | None]]:
        """Return a snapshot of per-host metrics."""
        # return a shallow copy for safety
        return {k: dict(v) for k, v in self._metrics.items()}

    # ---------- Cleanup ----------
    def close_host(self, host: str, user: str, port: int = 22):
        k = (host, user, port)
        with self._lock:
            ms = self._cache.pop(k, None)
            if ms:
                try:
                    ms.client.close()
                except Exception:
                    pass

    def close_idle(self):
        now = time.time()
        with self._lock:
            to_close = [k for k, ms in self._cache.items() if now - ms.last_used > self._idle_ttl_s]
            for k in to_close:
                try:
                    self._cache[k].client.close()
                except Exception:
                    pass
                self._cache.pop(k, None)

    def close_all(self):
        with self._lock:
            for k, ms in list(self._cache.items()):
                try:
                    ms.client.close()
                except Exception:
                    pass
                self._cache.pop(k, None)

    def stop(self):
        self._sweeper.stop()
        self._sweeper.join()
        self.close_all()


class _Sweeper(threading.Thread):
    """Background thread to close idle sessions periodically."""
    def __init__(self, mgr: SSHSessionManager, freq_s: int):
        super().__init__(daemon=True)
        self._mgr = mgr
        self._freq = freq_s
        self._run = True

    def stop(self):
        self._run = False

    def run(self):
        while self._run:
            time.sleep(self._freq)
            try:
                self._mgr.close_idle()
            except Exception:
                pass


# ---------- Minimal self-test ----------
if __name__ == "__main__":
    HOSTS = ["10.10.0.20", "10.10.0.30", "10.10.0.40"]
    USER = "root"
    KEY = "/home/glitch/.ssh/id_rsa"

    mgr = SSHSessionManager(idle_ttl_s=120)
    try:
        for h in HOSTS:
            r1 = mgr.exec(h, USER, KEY, "hostname")
            print(h, "→", r1["status"], "-", r1["message"], f"(retries={r1.get('retries', 0)}, latency={r1.get('latency_ms')}ms)")

        print("\nMetrics snapshot:")
        for k, v in mgr.metrics().items():
            print(k, "=>", v)

    finally:
        mgr.stop()


def _err(error_type: str, msg: str, exc: Exception, retries: int = 0) -> dict:
    return {
        "status": "failure",
        "exit_code": None,
        "stdout": "",
        "stderr": str(exc),
        "message": f"{msg}: {exc}",
        "error_type": error_type,
        "retries": retries,
    }
