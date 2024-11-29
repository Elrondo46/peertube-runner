#!/usr/bin/env python3
import click
import deepl

@click.command()
@click.argument('srt_file', type=click.Path(exists=True, readable=True))
@click.argument('target_lang')
@click.argument('output_file', type=click.Path(writable=True))
@click.option('--auth_key', prompt=True, hide_input=True, help='DeepL API authentication key.')
@click.option('--source_lang', default=None, help='Source language code (optional).')
@click.option('--glossary_id', default=None, help='Glossary ID for translation (optional).')
def translate_srt(srt_file, target_lang, output_file, auth_key, source_lang, glossary_id):
    """
    Translate an SRT file using the DeepL Python library and save the result.

    SRT_FILE: Path to the SRT file to be translated.
    TARGET_LANG: Target language code (e.g., 'EN', 'DE').
    OUTPUT_FILE: Path to save the translated SRT file.
    """
    try:
        # Initialize the DeepL Translator
        translator = deepl.Translator(auth_key)

        # Upload the document for translation
        with open(srt_file, 'rb') as file:
            click.echo("Uploading document for translation...")
            document_handle = translator.translate_document_upload(
                input_document=file,
                target_lang=target_lang,
                source_lang=source_lang,
                glossary=glossary_id,
            )
            click.echo(f"Document uploaded successfully. Document ID: {document_handle.document_id}")

        # Wait for the translation to complete
        click.echo("Waiting for translation to complete...")
        translator.translate_document_wait_until_done(document_handle)
        click.echo("Translation completed.")

        # Download the translated document
        click.echo(f"Downloading translated document to {output_file}...")
        with open(output_file, 'wb') as output_file_handle:
            translator.translate_document_download(document_handle, output_file_handle)
        click.echo(f"Translated document saved to {output_file}.")

    except deepl.DocumentTranslationException as e:
        click.echo(f"Error during translation: {e}")
    except deepl.DeepLException as e:
        click.echo(f"DeepL API error: {e}")
    except Exception as e:
        click.echo(f"Unexpected error: {e}")


if __name__ == '__main__':
    translate_srt()
