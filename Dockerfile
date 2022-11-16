FROM python:3.9-bullseye

LABEL author="Patrick Stöckle <patrick.stoeckle@posteo.de>"

ENV ELECTRON_DISABLE_SECURITY_WARNINGS "true"
ENV DRAWIO_DISABLE_UPDATE "true"
ENV DRAWIO_DESKTOP_COMMAND_TIMEOUT "10s"
ENV DRAWIO_DESKTOP_EXECUTABLE_PATH "/opt/drawio/drawio"
ENV DRAWIO_DESKTOP_RUNNER_COMMAND_LINE "/opt/drawio-desktop/runner.sh"
ENV XVFB_DISPLAY ":42"
ENV XVFB_OPTIONS ""
ENV DRAWIO_VERSION "20.3.0"

ENV PATH="${PATH}:/home/drawio-user/.local/bin"
ENV HOME=/home/drawio-user

WORKDIR "/opt/drawio-desktop"

COPY scripts/* ./

RUN set -e \
    && apt-get update -qq \
    && apt-get install --no-install-recommends -y -qq \
    bat \
    exa \
    libatspi2.0-0 \
    libasound2 \
    libgconf-2-4 \
    libgtk-3-0 \
    libnotify4 \
    libnss3 \
    libsecret-1-0 \
    libxss1 \
    libxtst6 \
    libgbm-dev \
    sgrep \
    wget \
    xdg-utils \
    xvfb  \
    zsh \
    && wget -q https://github.com/jgraph/drawio-desktop/releases/download/v${DRAWIO_VERSION}/drawio-amd64-${DRAWIO_VERSION}.deb  \
    && apt-get install -y /opt/drawio-desktop/drawio-amd64-${DRAWIO_VERSION}.deb  \
    && rm  /opt/drawio-desktop/drawio-amd64-${DRAWIO_VERSION}.deb  \
    && apt-get autoremove -y -qq  \
    && apt-get clean  \
    && rm -rf /var/lib/apt/lists/*  \
    && useradd --create-home --shell /bin/zsh drawio-user

WORKDIR /home/drawio-user
USER drawio-user

COPY --chown=drawio-user dist dist

RUN pip install --no-cache-dir --upgrade pip==22.3.1 \
    && pip install --no-cache-dir dist/*.whl \
    && rm -rf dist \
    && diagrams-net-automation --version
