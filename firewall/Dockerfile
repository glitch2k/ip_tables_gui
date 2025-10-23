# # FROM ubuntu:22.04

# # RUN apt update && apt install -y \
# #     iptables iproute2 tcpdump python3 python3-pip nano curl iputils-ping && apt clean

# # WORKDIR /app
# # COPY ./app /app
# # COPY ./db /db
# # RUN pip install rich

# # CMD ["bash"]

# # firewall/Dockerfile

# FROM ubuntu:22.04

# # Install base tools
# RUN apt update && apt install -y iptables iputils-ping openssh-server

# # Create SSH directory and enable the service
# RUN mkdir /var/run/sshd

# # Optional: set root password if needed (for debugging)
# # RUN echo 'root:root' | chpasswd

# # Copy in your public key (optional for dev environments)
# RUN mkdir -p /root/.ssh && chmod 700 /root/.ssh
# # COPY ./id_rsa.pub /root/.ssh/authorized_keys
# # RUN chmod 600 /root/.ssh/authorized_keys

# # Ensure SSH server starts automatically in the foreground
# CMD ["/usr/sbin/sshd", "-D"]



# firewall/Dockerfile

# FROM ubuntu:22.04

# # Install base packages
# RUN apt update && apt install -y iptables iputils-ping openssh-server vim net-tools

# # Prepare SSH runtime directory
# RUN mkdir -p /var/run/sshd

# # Configure SSH for key-based root login
# RUN echo "PubkeyAuthentication yes" >> /etc/ssh/sshd_config && \
#     echo "PasswordAuthentication no" >> /etc/ssh/sshd_config && \
#     echo "PermitRootLogin yes" >> /etc/ssh/sshd_config && \
#     mkdir -p /root/.ssh && chmod 700 /root/.ssh

# # Expose SSH port
# EXPOSE 22

# # Default command runs SSH in foreground (keeps container alive)
# CMD ["/usr/sbin/sshd", "-D"]

# firewall/Dockerfile

# FROM ubuntu:22.04

# # Install required packages
# RUN apt update && apt install -y iptables iputils-ping openssh-server vim net-tools

# # Prepare SSH runtime directory
# RUN mkdir -p /var/run/sshd

# # Configure SSH for key-based root login only
# RUN echo "PubkeyAuthentication yes" >> /etc/ssh/sshd_config && \
#     echo "PasswordAuthentication no" >> /etc/ssh/sshd_config && \
#     echo "PermitRootLogin yes" >> /etc/ssh/sshd_config && \
#     mkdir -p /root/.ssh && chmod 700 /root/.ssh

# # Expose port 22 internally (optional)
# EXPOSE 22

# # Start SSH in the foreground
# CMD ["/usr/sbin/sshd", "-D"]

# firewall/Dockerfile


# firewall/Dockerfile
FROM iptables_base:latest

# Install firewall-specific packages
RUN apt update && apt install -y iptables openssh-server && \
    mkdir -p /var/run/sshd && \
    echo "PubkeyAuthentication yes" >> /etc/ssh/sshd_config && \
    echo "PasswordAuthentication no" >> /etc/ssh/sshd_config && \
    echo "PermitRootLogin yes" >> /etc/ssh/sshd_config && \
    mkdir -p /root/.ssh && chmod 700 /root/.ssh

EXPOSE 22

CMD ["/usr/sbin/sshd", "-D"]

