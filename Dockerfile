# https://github.com/Chocobozzz/PeerTube/blob/v7.2.1/support/docker/production/Dockerfile.bookworm
FROM chocobozzz/peertube:v7.2.3-bookworm

RUN apt-get update && apt-get install -y \
    pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --break-system-packages whisper-ctranslate2
RUN npm install -g npm
RUN npm install -g @peertube/peertube-runner

WORKDIR /home/peertube/

ENV HOME=/home/peertube

# peertube
USER 999

# https://docs.joinpeertube.org/maintain/tools#peertube-runner
RUN npm install @peertube/peertube-runner

VOLUME [ "/home/peertube/.config/peertube-runner-nodejs/" ]
VOLUME [ "/home/peertube/.cache/peertube-runner-nodejs/" ]
VOLUME [ "/home/peertube/.local/share/peertube-runner-nodejs/" ]

ENTRYPOINT [ ]

CMD [ "npx", "peertube-runner" ]
