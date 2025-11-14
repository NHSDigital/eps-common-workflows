FROM mcr.microsoft.com/devcontainers/base:ubuntu

# provide DOCKER_GID via build args if you need to force group id to match host
ARG DOCKER_GID

# specify DOCKER_GID to force container docker group id to match host
RUN if [ -n "${DOCKER_GID}" ]; then \
      if ! getent group docker; then \
        groupadd -g ${DOCKER_GID} docker; \
      else \
        groupmod -g ${DOCKER_GID} docker; \
      fi && \
      usermod -aG docker vscode; \
    fi

# Anticipate and resolve potential permission issues with apt
RUN mkdir -p /tmp && chmod 1777 /tmp

RUN apt-get update \
    && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y dist-upgrade \
    && apt-get -y install --no-install-recommends htop vim curl git build-essential \
    libffi-dev libssl-dev libxml2-dev libxslt1-dev libjpeg8-dev libbz2-dev \
    zlib1g-dev unixodbc unixodbc-dev libsecret-1-0 libsecret-1-dev libsqlite3-dev \
    jq apt-transport-https ca-certificates gnupg-agent \
    software-properties-common bash-completion python3-pip make libbz2-dev \
    libreadline-dev libsqlite3-dev wget llvm libncurses5-dev libncursesw5-dev \
    xz-utils tk-dev liblzma-dev netcat-traditional libyaml-dev

USER vscode

# Install ASDF
RUN git clone https://github.com/asdf-vm/asdf.git ~/.asdf --branch v0.11.3 && \
    echo '. $HOME/.asdf/asdf.sh' >> ~/.bashrc && \
    echo '. $HOME/.asdf/completions/asdf.bash' >> ~/.bashrc

ENV PATH="$PATH:/home/vscode/.asdf/bin/:/workspaces/eps-prescription-tracker-ui/node_modules/.bin:/workspaces/eps-common-workflows/.venv/bin"

# Install ASDF plugins#
RUN asdf plugin add nodejs https://github.com/asdf-vm/asdf-nodejs.git && \
    asdf plugin add actionlint && \
    asdf plugin add shellcheck https://github.com/luizm/asdf-shellcheck.git && \
    asdf plugin add poetry https://github.com/asdf-community/asdf-poetry.git && \
    asdf plugin add python

WORKDIR /workspaces/eps-common-workflows

ADD .tool-versions /workspaces/eps-common-workflows/.tool-versions
ADD .tool-versions /home/vscode/.tool-versions

RUN asdf install python && \
    asdf install && \
    asdf reshim nodejs
