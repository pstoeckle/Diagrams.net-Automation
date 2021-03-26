FROM python:3.9-buster

WORKDIR "/opt/drawio-desktop"

ENV DRAWIO_VERSION "14.5.1"
RUN set -e; \
  apt-get update && apt-get install -y \
  libappindicator3-1 \
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
  xvfb;
RUN wget -q https://github.com/jgraph/drawio-desktop/releases/download/v${DRAWIO_VERSION}/drawio-amd64-${DRAWIO_VERSION}.deb
RUN apt-get install /opt/drawio-desktop/drawio-amd64-${DRAWIO_VERSION}.deb
RUN  rm -rf /opt/drawio-desktop/drawio-amd64-${DRAWIO_VERSION}.deb
RUN  rm -rf /var/lib/apt/lists/*;

COPY scripts/* ./

ENV ELECTRON_DISABLE_SECURITY_WARNINGS "true"
ENV DRAWIO_DISABLE_UPDATE "true"
ENV DRAWIO_DESKTOP_COMMAND_TIMEOUT "10s"
ENV DRAWIO_DESKTOP_EXECUTABLE_PATH "/opt/drawio/drawio"
ENV DRAWIO_DESKTOP_RUNNER_COMMAND_LINE "/opt/drawio-desktop/runner.sh"
ENV XVFB_DISPLAY ":42"
ENV XVFB_OPTIONS ""

RUN pip install --upgrade pip
COPY dist dist
RUN pip install dist/*.whl

RUN useradd --create-home --shell /bin/bash drawio_user
ENV HOME=/home/drawio_user
USER drawio_user
WORKDIR /home/drawio_user
