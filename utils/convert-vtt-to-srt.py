#!/usr/bin/env python3
import re
import click


def convert_vtt_to_srt(vtt_content):
  """
  Convert WebVTT content to SRT content.

  Args:
      vtt_content (str): Content of the WebVTT file.

  Returns:
      str: Converted SRT content.
  """
  # Remove WebVTT header if present
  vtt_content = re.sub(r"^(WEBVTT.*\n{2,4})", "", vtt_content, flags=re.MULTILINE)

  # Replace WebVTT timestamp format with SRT timestamp format
  srt_content = re.sub(
    r"(\d{2}:\d{2}:\d{2})\.(\d{3})",  # Match WebVTT timestamps (e.g., 00:00:01.000)
    r"\1,\2",  # Convert to SRT format (e.g., 00:00:01,000)
    vtt_content,
  )

  # Number captions sequentially
  segments = srt_content.split("\n\n")
  numbered_segments = []
  for i, segment in enumerate(segments, start=1):
    numbered_segment = f"{i}\n{segment.strip()}"
    numbered_segments.append(numbered_segment)

  return "\n\n".join(numbered_segments)


def convert_srt_to_vtt(srt_content):
    """
    Convert SRT content to WebVTT content.

    Args:
        srt_content (str): Content of the SRT file.

    Returns:
        str: Converted WebVTT content.
    """
    # Initialize WebVTT content with the header
    vtt_content = "WEBVTT\n\n"

    # Remove sequence numbers from SRT content
    srt_content = re.sub(r"^\d+\n", "", srt_content, flags=re.MULTILINE)

    # Replace SRT timestamp format with WebVTT timestamp format
    srt_content = re.sub(
        r"(\d{2}:\d{2}:\d{2}),(\d{3})",  # Match SRT timestamps (e.g., 00:00:01,000)
        r"\1.\2",  # Convert to WebVTT format (e.g., 00:00:01.000)
        srt_content,
    )

    # Append processed content to WebVTT header
    vtt_content += srt_content.strip()

    # Append trailing newline characters
    vtt_content += "\n\n"

    return vtt_content


@click.command()
@click.argument("vtt_file", type=click.Path(exists=True, readable=True))
@click.argument("srt_file", type=click.Path(writable=True))
def vtt_to_srt(vtt_file, srt_file):
  """
  Convert a WebVTT file to an SRT file.

  VTT_FILE: Path to the WebVTT file.
  SRT_FILE: Path where the SRT file will be written.
  """
  try:
    assert vtt_file.endswith(".vtt"), "Input file must be a WebVTT file"
    with open(vtt_file, "r", encoding="utf-8") as input_file:
      vtt_content = input_file.read()

    srt_content = convert_vtt_to_srt(vtt_content)
    reverted_vtt_content = convert_srt_to_vtt(srt_content)
    if reverted_vtt_content != vtt_content:
      click.echo("Warning: Conversion is not lossless. The resulting SRT file may differ from the original.")
      click.echo(f"Beginning...end of input WebVTT:  "
                 f"{repr(vtt_content[:50])}...{repr(vtt_content[-10:])}")
      click.echo(f"Beginning...end of converted SRT: "
                 f"{repr(srt_content[:50])}...{repr(srt_content[-10:])}")
      click.echo(f"Beginning...end of output WebVTT: "
                 f"{repr(reverted_vtt_content[:50])}...{repr(reverted_vtt_content[-10:])}")
      raise AssertionError("Conversion failed")

    assert srt_file.endswith(".srt"), "Output file must be a SRT file"
    with open(srt_file, "w", encoding="utf-8") as output_file:
      output_file.write(srt_content)

    click.echo(f"Converted '{vtt_file}' to '{srt_file}'")
  except Exception as e:
    click.echo(f"Error: {e}", err=True)


if __name__ == "__main__":
  vtt_to_srt()
