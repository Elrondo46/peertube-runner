# https://github.com/Chocobozzz/PeerTube/blob/v7.2.1/support/docker/production/Dockerfile.bookworm
FROM chocobozzz/peertube:v7.2.1-bookworm

RUN apt-get update && apt-get install -y \
    pipx \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /home/peertube/

ENV HOME=/home/peertube

# peertube
USER 999

# https://docs.joinpeertube.org/maintain/tools#peertube-runner
RUN pipx install whisper-ctranslate2 && pipx ensurepath
RUN npm install @peertube/peertube-runner@0.1.3

ENV PATH="${PATH}:/home/peertube/.local/bin"

VOLUME [ "/home/peertube/.config/peertube-runner-nodejs/" ]
VOLUME [ "/home/peertube/.cache/peertube-runner-nodejs/" ]
VOLUME [ "/home/peertube/.local/share/peertube-runner-nodejs/" ]

ENTRYPOINT [ ]

CMD [ "npx", "peertube-runner" ]
