FROM ubuntu:18.04

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
      python3 python3-pip libssl-dev pkg-config \
      libsqlite3-0 libsqlite3-dev apt-utils locales \
      python-pip-whl libleveldb-dev python3-setuptools \
      python3-dev pandoc python3-venv \
      libgmp-dev libbz2-dev libreadline-dev libsecp256k1-dev locales-all
RUN curl -sL https://deb.nodesource.com/setup_12.x | bash -
RUN apt-get -yy install nodejs
RUN locale-gen en_US.UTF-8
RUN python3 -m pip install -U pip

# Install .NET Core
RUN wget -q https://packages.microsoft.com/config/ubuntu/18.04/packages-microsoft-prod.deb -O packages-microsoft-prod.deb && \
    dpkg -i packages-microsoft-prod.deb && \
    apt-get update && apt-get -yy install dotnet-sdk-5.0 && \
    rm -f packages-microsoft-prod.deb
ENV DOTNET_CLI_TELEMETRY_OPTOUT=1

# Install Solidity compiler
WORKDIR /usr/bin
RUN wget https://github.com/ethereum/solidity/releases/download/v0.4.25/solc-static-linux
RUN mv solc-static-linux solc
RUN chmod +x solc

WORKDIR /root

# Install nodejs truffle web3 ganache-cli
RUN npm -g config set user root
RUN npm install -g truffle web3 ganache-cli

# Install go
RUN wget https://dl.google.com/go/go1.10.4.linux-amd64.tar.gz
RUN tar -xvf go1.10.4.linux-amd64.tar.gz
RUN mv go /usr/lib/go-1.10

# Install z3
RUN git clone https://github.com/Z3Prover/z3.git
WORKDIR /root/z3
RUN git checkout z3-4.8.6
RUN python3 scripts/mk_make.py --python
WORKDIR /root/z3/build
RUN make -j8
RUN make install

### Prepare a user account

RUN useradd -ms /bin/bash test
RUN usermod -aG sudo test
RUN echo "test ALL=(ALL:ALL) NOPASSWD:ALL" >> /etc/sudoers
USER test
WORKDIR /home/test

### Install smart contract testing tools
RUN mkdir /home/test/tools

# Install ilf
COPY --chown=test:test ./docker-setup/ilf/ /home/test/tools/ilf
ENV GOPATH=/home/test/tools/ilf/go
ENV GOROOT=/usr/lib/go-1.10
ENV PATH=$PATH:$GOPATH/bin
ENV PATH=$PATH:$GOROOT/bin
RUN /home/test/tools/ilf/install_ilf.sh
RUN mv /home/test/tools/ilf/preprocess \
       /home/test/tools/ilf/go/src/ilf/preprocess

# Install sFuzz
COPY --chown=test:test ./docker-setup/sFuzz /home/test/tools/sFuzz
RUN /home/test/tools/sFuzz/install_sFuzz.sh

# Install manticore
COPY --chown=test:test ./docker-setup/manticore/ /home/test/tools/manticore
RUN /home/test/tools/manticore/install_manticore.sh
ENV PATH /home/test/.local/bin:$PATH
ENV LD_LIBRARY_PATH=/usr/local/lib PREFIX=/usr/local HOST_OS=Linux

# Install mythril
COPY --chown=test:test ./docker-setup/mythril/ /home/test/tools/mythril
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.en
ENV LC_ALL en_US.UTF-8
RUN /home/test/tools/mythril/install_mythril.sh

# Install Smartian
RUN cd /home/test/tools/ && \
    git clone https://github.com/SoftSec-KAIST/Smartian.git && \
    cd Smartian && \
    git checkout v1.0 && \
    git submodule update --init --recursive && \
    make

# Add scripts for each tool
COPY --chown=test:test ./docker-setup/tool-scripts/ /home/test/scripts

### Prepare benchmarks

COPY --chown=test:test ./benchmarks /home/test/benchmarks

CMD ["/bin/bash"]
