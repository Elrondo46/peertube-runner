
`OwnTube-tv/peertube-runner/utils`
==================================

This directory contains utility scripts for dealing with PeerTube Runners and transcriptions.

Setup a virtualenv and install the requirements:

```bash
cd utils/
python3 -m venv venv
source venv/bin/activate
pip install click requests deepl sh
```


Authenticate with your PeerTube site
------------------------------------

Run the `issue-auth-token.py` script to issue a new authentication token:

```bash
export PT_HOSTNAME=my-peertube.com
export PT_USERNAME=my-username
export PT_PASSWORD=myP4ssw0rd
python3 issue-auth-token.py $PT_HOSTNAME $PT_USERNAME $PT_PASSWORD
```


Generate video captions (slowly)
--------------------------------

You can use your authentication token to run the `build-video-inventory.py` script to build
a video inventory from your PeerTube site:

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


Archive video metadata and captions
-----------------------------------

The `archive-video-metadata.py` script can be used to archive video metadata and captions in a Git
repository. This is useful for keeping a backup of your AI generated transcriptions.

```bash
export PT_HOSTNAME=my-peertube.com
export PT_TOKEN=$(jq -r .access_token data/auth-bearer-token.json)
python3 archive-video-metadata.py $PT_HOSTNAME $PT_TOKEN data/peertube-captions
```

The script will initialize a new Git repository in `data/peertube-captions` and commit the video
metadata and captions. Inspect the repository with `git status` and `git log`:

```bash
cd data/peertube-captions
git status
git log
cd ../..
```


Translate video captions using DeepL
------------------------------------

Register a DeepL API Free account at https://www.deepl.com/en/pro/change-plan#developer and
download your API key. Copy a WebVTT video caption file to the `data/` directory and run the
`convert-webvtt-to-srt.py` script to convert it to a DeepL compatible file format (SRT):

```bash
python3 convert-webvtt-to-srt.py data/my-video.vtt data/my-video.srt
```

Then run the `deepl-translate-srt.py` script to translate the SRT file to another language:

```bash
export DEEPL_API_KEY=my-deepl-api-key
python3 deepl-translate-srt.py data/my-video.srt EN-US data/my-video_en.srt --auth_key $DEEPL_API_KEY
```

The script will translate the SRT file to English (US) and save the translated file as
`data/my-video_en.srt`, convert it back to WebVTT format and save it as `data/my-video_en.vtt`:

```bash
python3 convert-srt-to-webvtt.py data/my-video_en.srt data/my-video_en.vtt
```

You can now attach the translated captions to your PeerTube video by choosing language and
uploading the new WebVTT file.
