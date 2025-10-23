# # server/Dockerfile
# FROM iptables_base:latest
# # Add any server-specific tools later
# CMD ["bash"]


FROM iptables_base:latest

RUN apt update && apt install -y openssh-server && \
    mkdir -p /var/run/sshd && \
    echo "PermitRootLogin yes" >> /etc/ssh/sshd_config && \
    echo "PubkeyAuthentication yes" >> /etc/ssh/sshd_config && \
    echo "PasswordAuthentication no" >> /etc/ssh/sshd_config && \
    mkdir -p /root/.ssh && chmod 700 /root/.ssh

EXPOSE 22

CMD ["/usr/sbin/sshd", "-D"]
