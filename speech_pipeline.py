import os

from dependency import create_blob_service_client

from config import validate_config

from utils import convert_to_wav, cleanup





def list_audio_files(blob_service_client, config):
    """
    Lists all supported audio files.
    """

    container_client = blob_service_client.get_container_client(
        config["audio_container"]
    )

    supported_extensions = (
        ".wav", ".mp3", ".m4a",
        ".flac", ".ogg", ".wma", ".aac"
    )

    audio_files = []

    for blob in container_client.list_blobs():
        if blob.name.lower().endswith(supported_extensions):
            audio_files.append(blob.name)

    return audio_files


def download_audio(blob_name, local_file, blob_service_client, config):
    """
    Downloads an audio file from Azure Blob Storage
    to the local machine.
    """

    container_client = blob_service_client.get_container_client(
        config["audio_container"]
    )

    blob_client = container_client.get_blob_client(blob_name)

    with open(local_file, "wb") as file:
        file.write(blob_client.download_blob().readall())

    return local_file

def prepare_audio(input_file, output_file):
    """
    Converts the downloaded audio file into
    a Speech-compatible WAV file.
    """

    convert_to_wav(input_file, output_file)

    return output_file

def transcribe_audio(audio_file, speech_config):
    """
    Transcribes a WAV file.
    """

    import azure.cognitiveservices.speech as speechsdk

    audio_config = speechsdk.audio.AudioConfig(
        filename=audio_file
    )

    recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config,
        audio_config=audio_config
    )

    result = recognizer.recognize_once()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return result.text

    elif result.reason == speechsdk.ResultReason.NoMatch:
        raise RuntimeError(
            "Azure Speech could not recognize any speech."
        )

    elif result.reason == speechsdk.ResultReason.Canceled:

        cancellation = result.cancellation_details

        raise RuntimeError(
            f"Speech recognition canceled: "
            f"{cancellation.reason} - "
            f"{cancellation.error_details}"
        )

    raise RuntimeError(
        f"Unexpected Speech recognition result: {result.reason}"
    )

def upload_transcript(
    transcript_text,
    blob_name,
    blob_service_client,
    config
):
    """
    Uploads transcript text to the Azure transcripts container.
    """

    container_client = blob_service_client.get_container_client(
        config["transcript_container"]
    )

    blob_client = container_client.get_blob_client(blob_name)

    blob_client.upload_blob(
        transcript_text,
        overwrite=True
    )

    return blob_name

def transcript_exists(
    blob_name,
    blob_service_client,
    config
):
    """
    Checks whether a transcript already exists.
    """

    container_client = blob_service_client.get_container_client(
        config["transcript_container"]
    )

    base_name = os.path.splitext(
        os.path.basename(blob_name)
    )[0]

    transcript_blob = f"{base_name}.txt"

    blob_client = container_client.get_blob_client(
        transcript_blob
    )

    return blob_client.exists()

def process_all_audio_files():
    """
    Processes all supported audio files from the Azure audio container.
    Creates shared dependencies once and reuses them for every file.
    """

    # Create shared dependencies ONCE
    config = validate_config()
    blob_service = create_blob_service_client()

    import azure.cognitiveservices.speech as speechsdk

    speech_config = speechsdk.SpeechConfig(
        subscription=config["speech_key"],
        region=config["speech_region"]
    )

    # Get all audio files
    audio_files = list_audio_files(blob_service, config)

    processed = 0
    skipped = 0
    failed = 0

    total = len(audio_files)

    print("\n=========================================")
    print(" Batch Processing")
    print("=========================================")
    print(f"Found {total} supported audio file(s).\n")

    if total == 0:
        print("No supported audio files found.")
        return {
            "processed": 0,
            "skipped": 0,
            "failed": 0
        }

    for index, audio_file in enumerate(audio_files, start=1):

        print(f"[{index}/{total}] {audio_file}")

        try:

            if transcript_exists(
                audio_file,
                blob_service,
                config
            ):
                print("   ⏭ Skipped (Transcript already exists)\n")
                skipped += 1
                continue

            process_audio_file(
                blob_name=audio_file,
                blob_service=blob_service,
                speech_config=speech_config,
                config=config
            )

            processed += 1
            print()

        except Exception as error:

            print(f"   ✗ Failed: {error}\n")
            failed += 1

    print("=========================================")
    print(" Batch Summary")
    print("=========================================")
    print(f"Processed : {processed}")
    print(f"Skipped   : {skipped}")
    print(f"Failed    : {failed}")
    print("=========================================")

    return {
        "processed": processed,
        "skipped": skipped,
        "failed": failed
    }

def process_audio_file(blob_name, blob_service, config,speech_config):
    """
    Processes one audio file from Azure Blob Storage.

    Steps:
    1. Download audio
    2. Convert to WAV
    3. Transcribe using Azure Speech
    4. Upload transcript
    5. Clean up temporary files

    Parameters
    ----------
    blob_name : str
        Name of the audio blob.
    blob_service : BlobServiceClient
        Injected Azure Blob Storage client.
    config : dict
        Validated application configuration.
    """

    base_name = os.path.splitext(os.path.basename(blob_name))[0]

    local_audio = f"temp_input_{os.path.basename(blob_name)}"
    local_wav = f"temp_output_{base_name}.wav"

    try:
        print(f"\nProcessing: {blob_name}")

        # Step 1: Download original audio
        download_audio(
            blob_name=blob_name,
            local_audio=local_audio,
            blob_service=blob_service,
            config=config
        )
        print("  ✓ Audio downloaded")

        # Step 2: Convert to Speech-compatible WAV
        prepare_audio(local_audio, local_wav)
        print("  ✓ Audio converted")

        # Step 3: Transcribe audio
        transcript = transcribe_audio(local_wav,speech_config)
        print("  ✓ Audio transcribed")

        # Step 4: Create transcript filename
        transcript_blob = f"{base_name}.txt"

        # Step 5: Upload transcript
        upload_transcript(
            transcript=transcript,
            transcript_blob=transcript_blob,
            blob_service=blob_service,
            config=config
        )
        print(f"  ✓ Transcript uploaded: {transcript_blob}")

        return True

    finally:
        # Step 6: Always clean up temporary files
        cleanup(local_audio, local_wav)