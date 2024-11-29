#!/usr/bin/env python3
import re
import click


def convert_webvtt_to_srt(webvtt_content):
  """
  Convert WebVTT content to SRT content.

  Args:
      webvtt_content (str): Content of the WebVTT file.

  Returns:
      str: Converted SRT content.
  """
  # Remove WebVTT header if present
  webvtt_content = re.sub(r"^(WEBVTT.*\n\n\n\n)", "", webvtt_content, flags=re.MULTILINE)

  # Replace WebVTT timestamp format with SRT timestamp format
  srt_content = re.sub(
    r"(\d{2}:\d{2}:\d{2})\.(\d{3})",  # Match WebVTT timestamps (e.g., 00:00:01.000)
    r"\1,\2",  # Convert to SRT format (e.g., 00:00:01,000)
    webvtt_content,
  )

  # Number captions sequentially
  segments = srt_content.split("\n\n")
  numbered_segments = []
  for i, segment in enumerate(segments, start=1):
    numbered_segment = f"{i}\n{segment.strip()}"
    numbered_segments.append(numbered_segment)

  return "\n\n".join(numbered_segments)


@click.command()
@click.argument("webvtt_file", type=click.Path(exists=True, readable=True))
@click.argument("srt_file", type=click.Path(writable=True))
def webvtt_to_srt(webvtt_file, srt_file):
  """
  Convert a WebVTT file to an SRT file.

  WEBVTT_FILE: Path to the WebVTT file.
  SRT_FILE: Path where the SRT file will be written.
  """
  try:
    with open(webvtt_file, "r", encoding="utf-8") as input_file:
      webvtt_content = input_file.read()

    srt_content = convert_webvtt_to_srt(webvtt_content)

    with open(srt_file, "w", encoding="utf-8") as output_file:
      output_file.write(srt_content)

    click.echo(f"Converted {webvtt_file} to {srt_file}")
  except Exception as e:
    click.echo(f"Error: {e}", err=True)


if __name__ == "__main__":
  webvtt_to_srt()
