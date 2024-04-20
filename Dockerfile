FROM ubuntu:20.04

WORKDIR /root/

### Install packages and utilities

# You may replace the URL for into a faster one in your region.
# RUN sed -i 's/archive.ubuntu.com/ftp.daumkakao.com/g' /etc/apt/sources.list
ENV DEBIAN_FRONTEND="noninteractive"

RUN apt-get update && \
    apt-get -yy install \
      wget apt-transport-https git unzip \
      build-essential libtool libtool-bin gdb \
      automake autoconf bison flex python sudo vim \
      curl software-properties-common \
      python3 python3-pip libssl-dev pkg-config libffi-dev\
      libsqlite3-0 libsqlite3-dev apt-utils locales \
      python-pip-whl libleveldb-dev python3-setuptools \
      python3-dev pandoc python3-venv \
      libgmp-dev libbz2-dev libreadline-dev libsecp256k1-dev locales-all
RUN curl -sL https://deb.nodesource.com/setup_12.x | bash -
RUN apt-get -yy install nodejs
RUN locale-gen en_US.UTF-8
RUN python3 -m pip install -U pip

# Install .NET Core
RUN wget https://packages.microsoft.com/config/ubuntu/20.04/packages-microsoft-prod.deb -O packages-microsoft-prod.deb && \
    dpkg -i packages-microsoft-prod.deb && \
    apt-get update && apt-get -yy install dotnet-sdk-8.0 && \
    rm -f packages-microsoft-prod.deb
ENV DOTNET_CLI_TELEMETRY_OPTOUT=1

# Install Solidity compiler
WORKDIR /usr/bin
RUN wget https://github.com/ethereum/solidity/releases/download/v0.4.25/solc-static-linux
RUN mv solc-static-linux solc
RUN chmod +x solc

WORKDIR /root

### Prepare a user account

RUN useradd -ms /bin/bash test
RUN usermod -aG sudo test
RUN echo "test ALL=(ALL:ALL) NOPASSWD:ALL" >> /etc/sudoers
USER test
WORKDIR /home/test

### Install smart contract testing tools
RUN mkdir /home/test/tools

# Install sFuzz
COPY --chown=test:test ./docker-setup/sFuzz /home/test/tools/sFuzz
RUN /home/test/tools/sFuzz/install_sFuzz.sh

# Install mythril
COPY --chown=test:test ./docker-setup/mythril/ /home/test/tools/mythril
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.en
ENV LC_ALL en_US.UTF-8
RUN /home/test/tools/mythril/install_mythril.sh

# Install Smartian (commit badd4ff, which successfully runs on Ubuntu 20.04)
RUN cd /home/test/tools/ && \
    git clone https://github.com/SoftSec-KAIST/Smartian.git && \
    cd Smartian && \
    git checkout badd4ff && \
    git submodule update --init --recursive && \
    make

# Add scripts for each tool
COPY --chown=test:test ./docker-setup/tool-scripts/ /home/test/scripts

### Prepare benchmarks

COPY --chown=test:test ./benchmarks /home/test/benchmarks

CMD ["/bin/bash"]
