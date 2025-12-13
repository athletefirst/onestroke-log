# See here for image contents: https://github.com/devcontainers/images/tree/main/src/python
# Available image variants: https://github.com/devcontainers/templates/blob/main/src/python/devcontainer-template.json
ARG VARIANT="3"
FROM mcr.microsoft.com/devcontainers/python:1-${VARIANT}-bookworm

# [Option] Install Node.js
# ARG INSTALL_NODE="true"
# ARG NODE_VERSION="lts/*"
# RUN if [ "${INSTALL_NODE}" = "true" ]; then su vscode -c "umask 0002 && . /usr/local/share/nvm/nvm.sh && nvm install ${NODE_VERSION} 2>&1"; fi

# [Optional] If your pip requirements rarely change, uncomment this section to add them to the image.
# COPY requirements.txt /tmp/pip-tmp/
# RUN pip3 --disable-pip-version-check --no-cache-dir install -r /tmp/pip-tmp/requirements.txt \
#     && rm -rf /tmp/pip-tmp

# [Optional] Uncomment this section to install additional OS packages.
# RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
#     && apt-get -y install --no-install-recommends <your-package-list-here>

# [Optional] Uncomment this line to install global node packages.
# RUN su vscode -c "source /usr/local/share/nvm/nvm.sh && npm install -g <your-package-here>" 2>&1

# Create directory and set permission.
RUN mkdir /home/vscode/dev \ 
    && chown -R vscode:vscode /home/vscode/dev

# Install dev requirements
COPY ./dev/requirements_dev.txt /tmp/pip-tmp/
RUN pip3 --disable-pip-version-check --no-cache-dir install --upgrade -r /tmp/pip-tmp/requirements_dev.txt \
    && rm -rf /tmp/pip-tmp

# Install UV (Astral) and Marimo
USER vscode
WORKDIR /home/vscode
RUN curl -LsSf https://astral.sh/uv/install.sh | sh \
    && .local/bin/uv tool install marimo
