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
@click.argument("srt_file", type=click.Path(exists=True, readable=True))
@click.argument("vtt_file", type=click.Path(writable=True))
def srt_to_vtt(srt_file, vtt_file):
    """
    Convert an SRT file to a WebVTT file.

    SRT_FILE: Path to the SRT file.
    VTT_FILE: Path where the WebVTT file will be written.
    """
    try:
        assert srt_file.endswith(".srt"), "Input file must be an SRT file"
        with open(srt_file, "r", encoding="utf-8") as input_file:
            srt_content = input_file.read()

        vtt_content = convert_srt_to_vtt(srt_content)
        reverted_srt_content = convert_vtt_to_srt(vtt_content)
        if reverted_srt_content != srt_content:
          click.echo(
            "Warning: Conversion is not lossless. The resulting WebVTT file may differ from the original.")
          click.echo(f"Beginning...end of input SRT:        "
                     f"{repr(srt_content[:50])}...{repr(srt_content[-10:])}")
          click.echo(f"Beginning...end of converted WebVTT: "
                     f"{repr(vtt_content[:50])}...{repr(vtt_content[-10:])}")
          click.echo(f"Beginning...end of output SRT:       "
                     f"{repr(reverted_srt_content[:50])}...{repr(reverted_srt_content[-10:])}")
          # check if convert anyway
          if not click.confirm("Do you want to proceed with the conversion?", default=False):
            raise AssertionError("Conversion failed")

        assert vtt_file.endswith(".vtt"), "Output file must be a WebVTT file"
        with open(vtt_file, "w", encoding="utf-8") as output_file:
            output_file.write(vtt_content)

        click.echo(f"Converted '{srt_file}' to '{vtt_file}'")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


if __name__ == "__main__":
    srt_to_vtt()
