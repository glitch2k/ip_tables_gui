"""
Module: ssh_file_transfer
Phase: 3
Milestone: 3
Step: 4
Purpose:
    Provide secure file upload/download utilities over existing SSHSessionManager sessions.
    Reuses cached Paramiko clients from SSHSessionManager to avoid reconnect overhead.
"""

from __future__ import annotations
import os
from typing import Dict
import paramiko
from app.core.ssh_session_manager import SSHSessionManager, _err


class SSHFileTransfer:
    """Wrapper that performs upload/download through an SSHSessionManager."""

    def __init__(self, manager: SSHSessionManager):
        self.manager = manager

    def upload(self, host: str, user: str, key_path: str, local_path: str, remote_path: str) -> Dict[str, str]:
        """Upload a file to remote host."""
        try:
            client = self.manager.get_session(host, user, key_path)
            sftp = client.open_sftp()
            sftp.put(local_path, remote_path)
            sftp.close()
            return {
                "status": "success",
                "message": f"Uploaded {os.path.basename(local_path)} → {host}:{remote_path}",
            }
        except Exception as e:
            return _err("SFTPError", f"SFTP upload failed to {host}", e)

    def download(self, host: str, user: str, key_path: str, remote_path: str, local_path: str) -> Dict[str, str]:
        """Download a file from remote host."""
        try:
            client = self.manager.get_session(host, user, key_path)
            sftp = client.open_sftp()
            sftp.get(remote_path, local_path)
            sftp.close()
            return {
                "status": "success",
                "message": f"Downloaded {host}:{remote_path} → {local_path}",
            }
        except Exception as e:
            return _err("SFTPError", f"SFTP download failed from {host}", e)


# ---------- self-test ----------
if __name__ == "__main__":
    mgr = SSHSessionManager()
    xfer = SSHFileTransfer(mgr)

    HOST = "10.10.0.20"
    USER = "root"
    KEY = "/home/glitch/.ssh/id_rsa"

    print("Uploading test file...")
    open("sample_upload.txt", "w").write("Firewall test config\n")
    res1 = xfer.upload(HOST, USER, KEY, "sample_upload.txt", "/root/sample_upload.txt")
    print(res1)

    print("\nDownloading same file back...")
    res2 = xfer.download(HOST, USER, KEY, "/root/sample_upload.txt", "downloaded_test.txt")
    print(res2)

    mgr.stop()
