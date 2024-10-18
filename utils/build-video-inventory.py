#!/usr/bin/env python3
import json
import os
import click
import requests


def _get_all_videos(hostname, bearer_token):
  """Fetch all videos from the API in batches of 100."""
  url = f'https://{hostname}/api/v1/videos'
  headers = {
    'Authorization': f'Bearer {bearer_token}',
    'Accept': 'application/json'
  }

  # Parameters that will be used in each request
  params = {
    'sort': 'publishedAt',
    'nsfw': 'both',
    'isLocal': 'true',
    'include': '111',
    'privacyOneOf': [1, 2, 3, 4, 5],
    'count': 100,
    'start': 0  # Start with the first video
  }

  all_videos = []

  while True:
    try:
      # Make the API request
      response = requests.get(url, headers=headers, params=params)
      response.raise_for_status()
      data = response.json()

      # Check if there are any videos in the response
      videos = data.get('data', [])
      if not videos:
        break  # No more videos to fetch

      # Append the fetched videos to the list
      all_videos.extend(videos)

      # Update the 'start' parameter for the next batch
      params['start'] += len(videos)

      click.echo(click.style(f"Fetched {len(videos)} videos, total: {len(all_videos)}", fg='green'))

    except requests.exceptions.RequestException as e:
      click.echo(click.style(f"Error: {e}", fg='red'))
      exit(1)

  return all_videos


def _get_video_subtitles(hostname, bearer_token, video_uuid):
  """Fetch subtitles for a specific video."""
  url = f'https://{hostname}/api/v1/videos/{video_uuid}/captions'
  headers = {
    'Authorization': f'Bearer {bearer_token}',
    'Accept': 'application/json'
  }

  try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    subtitles = data.get('data', [])
    return subtitles
  except requests.exceptions.RequestException as e:
    click.echo(click.style(f"Error: {e}", fg='red'))
    return None


@click.command()
@click.argument('hostname')
@click.argument('bearer_token')
def build_video_inventory(hostname, bearer_token):
  """Fetch all videos, then check each for if it has subtitles or not."""

  os.makedirs('data', exist_ok=True)

  all_videos_inventory_path = 'data/video-inventory.json'
  if os.path.exists(all_videos_inventory_path):
    click.echo(click.style(f"Inventory file {all_videos_inventory_path} already exists, loading data form file.",
                           fg='green'))
    with open('data/video-inventory.json', 'r') as all_videos_file:
      all_videos = json.load(all_videos_file)
  else:
    click.echo(click.style(f"Inventory file {all_videos_inventory_path} missing, loading data from API.",
                           fg='yellow'))
    all_videos = _get_all_videos(hostname, bearer_token)
    with open('data/video-inventory.json', 'w') as all_videos_file:
      all_videos_file.write(json.dumps(all_videos, indent=2))
  click.echo(click.style(f"Full video inventory loaded with {len(all_videos)} videos.", fg='green'))

  # Check each video for subtitles
  videos_with_subtitles = []
  videos_without_subtitles = []
  for idx, video in enumerate(all_videos):
    subtitles = _get_video_subtitles(hostname, bearer_token, video['uuid'])
    if subtitles:
      videos_with_subtitles.append(video)
      click.echo(click.style(f"Video {str(idx).zfill(4)}/{len(all_videos)} {video['uuid']} has {len(subtitles)} "
                             f"subtitles (total WITH {len(videos_with_subtitles)}).", fg='green'))
    else:
      videos_without_subtitles.append(video)
      click.echo(
        click.style(f"Video {str(idx).zfill(4)}/{len(all_videos)} {video['uuid']} has {len(subtitles)} subtitles "
                    f"(total WITHOUT {len(videos_without_subtitles)}).", fg='yellow'))

  # Dump to JSON files
  videos_by_subtitles_path = 'data/video-inventory-by-subtitles.json'
  with open(videos_by_subtitles_path, 'w') as videos_by_subtitles_file:
    videos_by_subtitles_file.write(json.dumps({
      'videos_without_subtitles': videos_without_subtitles,
      'videos_to_generate_subtitles': [],
      'videos_with_subtitles': videos_with_subtitles
    }, indent=2))
  click.echo(click.style(f"Full video inventory saved to {videos_by_subtitles_path}, "
                         f"{len(videos_without_subtitles)} videos without subtitles and {len(videos_with_subtitles)} "
                         f"with subtitles.", fg='green'))


if __name__ == '__main__':
  build_video_inventory()
