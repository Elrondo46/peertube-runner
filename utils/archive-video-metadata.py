#!/usr/bin/env python3
import json
import os
from datetime import datetime

import click
import requests
import sh


@click.command()
@click.argument('hostname')
@click.argument('bearer_token')
@click.argument('output_dir')
def archive_videos(hostname, bearer_token, output_dir='data/peertube-captions'):
  """Check videos from the `data/video-inventory-by-subtitles.json:videos_with_subtitles` and archive to disk."""

  # Find videos that have been transcribed successfully
  videos_by_subtitles_path = 'data/video-inventory-by-subtitles.json'
  with open(videos_by_subtitles_path, 'r') as videos_by_subtitles_file:
    videos_by_subtitles = json.loads(videos_by_subtitles_file.read())

  if not videos_by_subtitles['videos_with_subtitles']:
    click.echo(click.style("No videos with subtitles found.", fg='yellow'))
    exit(0)
  else:
    if not os.path.exists(output_dir):
      os.makedirs(output_dir, exist_ok=True)
      sh.git('init', _cwd=output_dir)
      click.echo(click.style(f"Initialized git repository in {output_dir}.", fg='yellow'))
    for video in videos_by_subtitles['videos_with_subtitles']:
      click.echo(click.style(f"Found video UUID {video['uuid']} with transcription."))
      subtitles = video['captions']

      if subtitles['total'] and subtitles['data'][0]['captionPath'].endswith('.vtt'):
        # Parse the publishing date for archiving path
        published_at = datetime.fromisoformat(video['publishedAt'])
        published_yymmdd = published_at.strftime('%y%m%d')
        click.echo(
          click.style(f'Found subtitles for video {video['uuid']}, "{video['name']}": {subtitles}.', fg='green'))
        base_path = f'{hostname}/{published_at.strftime('%Y/%m/%d')}'
        os.makedirs(f'{output_dir}/{base_path}', exist_ok=True)
        video_json_path = f'{base_path}/{video["uuid"]}.json'
        video_vtt_path = f'{base_path}/{video["uuid"]}.vtt'
        if os.path.exists(f'{output_dir}/{video_json_path}') and os.path.exists(f'{output_dir}/{video_vtt_path}'):
          continue
        captions_text = requests.get(f'https://{hostname}{subtitles['data'][0]['captionPath']}').text
        assert 'WEBVTT' in captions_text, f'Failed to fetch captions for video {video["uuid"]}'
        subtitles['data'][0]['captionTextVTT'] = captions_text
        commit_video_json, commit_video_vtt = False, False
        if not os.path.exists(f'{output_dir}/{video_json_path}'):
          click.echo(click.style(f'Archiving video metadata as "{video_json_path}"', fg='black'))
          video['captions'] = subtitles
          with open(f'{output_dir}/{video_json_path}', 'w', encoding='utf-8') as video_json_file:
            video_json_file.write(json.dumps(video, indent=2))
          commit_video_json = True
        if not os.path.exists(f'{output_dir}/{video_vtt_path}'):
          click.echo(click.style(f'Archiving video subtitles as "{video_vtt_path}"', fg='black'))
          with open(f'{output_dir}/{video_vtt_path}', 'w', encoding='utf-8') as video_vtt_file:
            video_vtt_file.write(captions_text)
          commit_video_vtt = True
        if commit_video_json and commit_video_vtt:
          sh.git('add', video_json_path, video_vtt_path, _cwd=output_dir)
          sh.git('status', _cwd=output_dir)
          sh.git('commit', '-m', f'{published_yymmdd}: Add "{video["name"]}"\n'
                                 f'\n'
                                 f'Initial metadata and subtitles archiving for '
                                 f'https://{hostname}/w/{video['uuid']}\n', _cwd=output_dir)
      else:
        click.echo(click.style(f'Failed to get subtitles for video {video['uuid']}, '
                               f'"{video['name']}": {subtitles}.', fg='yellow'))


if __name__ == '__main__':
  archive_videos()
