#!/usr/bin/env python3
import re
import click


def convert_srt_to_webvtt(srt_content):
    """
    Convert SRT content to WebVTT content.

    Args:
        srt_content (str): Content of the SRT file.

    Returns:
        str: Converted WebVTT content.
    """
    # Initialize WebVTT content with the header
    webvtt_content = "WEBVTT\n\n\n\n"

    # Remove sequence numbers from SRT content
    srt_content = re.sub(r"^\d+\n", "", srt_content, flags=re.MULTILINE)

    # Replace SRT timestamp format with WebVTT timestamp format
    srt_content = re.sub(
        r"(\d{2}:\d{2}:\d{2}),(\d{3})",  # Match SRT timestamps (e.g., 00:00:01,000)
        r"\1.\2",  # Convert to WebVTT format (e.g., 00:00:01.000)
        srt_content,
    )

    # Append processed content to WebVTT header
    webvtt_content += srt_content.strip()

    # Append trailing newline characters
    webvtt_content += "\n\n"

    return webvtt_content


@click.command()
@click.argument("srt_file", type=click.Path(exists=True, readable=True))
@click.argument("webvtt_file", type=click.Path(writable=True))
def srt_to_webvtt(srt_file, webvtt_file):
    """
    Convert an SRT file to a WebVTT file.

    SRT_FILE: Path to the SRT file.
    WEBVTT_FILE: Path where the WebVTT file will be written.
    """
    try:
        with open(srt_file, "r", encoding="utf-8") as input_file:
            srt_content = input_file.read()

        webvtt_content = convert_srt_to_webvtt(srt_content)

        with open(webvtt_file, "w", encoding="utf-8") as output_file:
            output_file.write(webvtt_content)

        click.echo(f"Converted {srt_file} to {webvtt_file}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


if __name__ == "__main__":
    srt_to_webvtt()
