
`OwnTube-tv/peertube-runner/utils`
==================================

This directory contains utility scripts for dealing with PeerTube Runners.

Setup a virtualenv and install the requirements:

```bash
cd utils/
python3 -m venv venv
source venv/bin/activate
pip install click requests
```

Then you can run the `issue-auth-token.py` script to issue a new authentication token:

```bash
export PT_HOSTNAME=my-peertube.com
export PT_USERNAME=my-username
export PT_PASSWORD=myP4ssw0rd
python3 issue-auth-token.py $PT_HOSTNAME $PT_USERNAME $PT_PASSWORD
```

Now you can use the token to run the `build-video-inventory.py` script to build a video inventory
from your PeerTube site:

```bash
export PT_HOSTNAME=my-peertube.com
export PT_TOKEN=$(jq -r .access_token data/auth-bearer-token.json)
python3 build-video-inventory.py $PT_HOSTNAME $PT_TOKEN
```

After the inventory JSON files in `data/` are created, run the `slow-jobs-scheduling.py`
script to schedule pending (transcription) jobs at a slow pace:

```bash
export PT_HOSTNAME=my-peertube.com
export PT_TOKEN=$(jq -r .access_token data/auth-bearer-token.json)
python3 slow-jobs-scheduling.py $PT_HOSTNAME $PT_TOKEN
```

You can run this as a cron job to schedule jobs at a slow pace 24/7, or you run it as
a simple shell loop in `tmux`, like so:

```bash
export PT_HOSTNAME=my-peertube.com
while true; do
    export PT_TOKEN=$(jq -r .access_token data/auth-bearer-token.json)
    python3 slow-jobs-scheduling.py $PT_HOSTNAME $PT_TOKEN
    sleep 600
done
```
