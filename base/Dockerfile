# base/Dockerfile
FROM ubuntu:22.04

# Install essential networking utilities
RUN apt update && apt install -y \
    iputils-ping \
    net-tools \
    curl \
    vim \
    openssh-client && \
    apt clean && rm -rf /var/lib/apt/lists/*

# Set a default work directory
WORKDIR /root

# Default command keeps container open
CMD ["bash"]
