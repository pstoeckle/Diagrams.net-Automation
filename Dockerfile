FROM python:3.9-bullseye

ARG COMMIT=""
ARG COMMIT_SHORT=""
ARG BRANCH=""
ARG TAG=""

LABEL author="Patrick Stöckle <patrick.stoeckle@tum.de>"
LABEL edu.tum.i4.diagrams-net-automation.commit=${COMMIT}
LABEL edu.tum.i4.diagrams-net-automation.commit-short=${COMMIT_SHORT}
LABEL edu.tum.i4.diagrams-net-automation.branch=${BRANCH}
LABEL edu.tum.i4.diagrams-net-automation.tag=${TAG}

ENV COMMIT=${COMMIT}
ENV COMMIT_SHORT=${COMMIT_SHORT}
ENV BRANCH=${BRANCH}
ENV TAG=${TAG}

ENV ELECTRON_DISABLE_SECURITY_WARNINGS "true"
ENV DRAWIO_DISABLE_UPDATE "true"
ENV DRAWIO_DESKTOP_COMMAND_TIMEOUT "10s"
ENV DRAWIO_DESKTOP_EXECUTABLE_PATH "/opt/drawio/drawio"
ENV DRAWIO_DESKTOP_RUNNER_COMMAND_LINE "/opt/drawio-desktop/runner.sh"
ENV XVFB_DISPLAY ":42"
ENV XVFB_OPTIONS ""
ENV DRAWIO_VERSION "16.5.1"

COPY sources.list /etc/apt/sources.list

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

COPY dist dist

RUN chown drawio-user dist

USER drawio-user

RUN pip install --no-cache-dir --upgrade pip==21.3.1 \
    && pip install --no-cache-dir dist/*.whl \
    && rm -rf dist

ENV PATH="${PATH}:/home/drawio-user/.local/bin"
ENV HOME=/home/drawio-user

RUN diagrams-net-automation --version

