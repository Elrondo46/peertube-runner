#!/usr/bin/env python3
import json
from datetime import datetime

import click
import requests


def _get_active_jobs(hostname, bearer_token):
  """Fetch remote runner jobs that are not in state 'Completed' or 'Errored', i.e. active."""
  url = f'https://{hostname}/api/v1/runners/jobs?start=0&count=100&sort=-createdAt'
  headers = {
    'Authorization': f'Bearer {bearer_token}',
    'Accept': 'application/json'
  }

  try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    pending_or_running_jobs = [job for job in data['data'] if job['state']['label'] not in ['Completed', 'Errored']]
    click.echo(click.style(f"Response: Got {len(pending_or_running_jobs)} pending/running jobs from {url}",
                           fg='green'))
    for job in pending_or_running_jobs:
      runner_name = 'n/a' if not job['runner'] else job['runner']['name']
      video_uuid = job['privatePayload']['videoUUID']
      state = job['state']['label'] if len(job['state']['label']) <= 10 else job['state']['label'][:7] + '...'
      created_at = datetime.strptime(job['createdAt'], '%Y-%m-%dT%H:%M:%S.%fZ')
      updated_at = datetime.strptime(job['updatedAt'], '%Y-%m-%dT%H:%M:%S.%fZ')
      duration = (updated_at - created_at).total_seconds()
      click.echo(click.style(f"Job UUID: {job['uuid']} | Video UUID: {video_uuid} | "
                             f"Type: {job['type'].ljust(25)} | "
                             f"State: {state} | "
                             f"Runner: {runner_name.ljust(23)} | "
                             f"CreatedAt: {job['createdAt']} | "
                             f"UpdatedAt: {job['updatedAt']} | "
                             f"Duration: {duration:.0f} sec",
                             fg='green'))
    return pending_or_running_jobs
  except requests.exceptions.RequestException as e:
    click.echo(click.style(f"Error: {e}", fg='red'))
    exit(1)


def _generate_video_subtitles(hostname, bearer_token, video_uuid):
  """Create a new job to generate subtitles for a video."""
  url = f'https://{hostname}/api/v1/videos/{video_uuid}/captions/generate'
  headers = {
    'Authorization': f'Bearer {bearer_token}',
    'Content-Type': 'application/json'
  }

  try:
    response = requests.post(url, None, json={}, headers=headers)
    response.raise_for_status()
    return response.status_code
  except requests.exceptions.RequestException as e:
    click.echo(click.style(f"Error: {e}", fg='red'))
    return e.response.status_code


@click.command()
@click.argument('hostname')
@click.argument('bearer_token')
def check_and_schedule_slowly(hostname, bearer_token):
  """Check active Runner jobs and back-fill with new `video-transcription` jobs on low activity."""

  pending_or_running_jobs = _get_active_jobs(hostname, bearer_token)
  if len(pending_or_running_jobs) >= 4:
    click.echo(click.style("Slow-job scheduling quota already full (max 4 jobs), exiting.", fg='yellow'))
    exit(0)

  # Find videos that have not been transcribed yet
  videos_by_subtitles_path = 'data/video-inventory-by-subtitles.json'
  with open(videos_by_subtitles_path, 'r') as videos_by_subtitles_file:
    videos_by_subtitles = json.loads(videos_by_subtitles_file.read())

  if not videos_by_subtitles['videos_without_subtitles']:
    click.echo(click.style("No videos found that need transcription.", fg='yellow'))
    exit(0)
  else:
    video = videos_by_subtitles['videos_without_subtitles'].pop()
    click.echo(click.style(f"Found video UUID {video['uuid']} that need transcription.", fg='green'))
    videos_by_subtitles['videos_to_generate_subtitles'].append(video)
    job_status = _generate_video_subtitles(hostname, bearer_token, video['uuid'])
    if 200 <= job_status < 300:
      click.echo(click.style(f"Created job with status code {job_status} for video {video['uuid']}.", fg='green'))
    else:
      click.echo(click.style(f"Failed to create job for video {video['uuid']} with status code {job_status}.",
                             fg='yellow'))
    with open(videos_by_subtitles_path, 'w') as videos_by_subtitles_file:
      videos_by_subtitles_file.write(json.dumps(videos_by_subtitles, indent=2))


if __name__ == '__main__':
  check_and_schedule_slowly()
