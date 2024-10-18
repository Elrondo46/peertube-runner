
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

Then you can run the `build-video-inventory.py` script to build a video inventory from
your PeerTube site:

```bash
python3 build-video-inventory.py <hostname> <bearer_token>
```

After the inventory JSON files in `data/` are created, run the `slow-jobs-scheduling.py`
script to schedule pending (transcription) jobs at a slow pace:

```bash
python3 slow-jobs-scheduling.py <hostname> <bearer_token>
```

You can run this as a cron job to schedule jobs at a slow pace 24/7, or you run it as
a simple shell loop in `tmux`, like so:

```bash
export PT_HOSTNAME=my-peertube.com
export PT_TOKEN="e16e3a1...29914d4"
while true; do
    python3 slow-jobs-scheduling.py $PT_HOSTNAME $PT_TOKEN
    sleep 600
done
```
