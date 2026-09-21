import os

from azure.storage.blob import BlobServiceClient

from config import validate_config

from utils import convert_to_wav, cleanup


def get_blob_service_client():
    """
    Creates and returns an Azure Blob Storage client.
    """

    config = validate_config()

    return BlobServiceClient.from_connection_string(
        config["connection_string"]
    )


def list_audio_files():
    """
    Lists all audio files available in the Azure audio container.
    """

    config = validate_config()
    blob_service_client = get_blob_service_client()

    container_client = blob_service_client.get_container_client(
        config["audio_container"]
    )

    supported_extensions = (
        ".wav",
        ".mp3",
        ".m4a",
        ".flac",
        ".ogg",
        ".wma",
        ".aac",
    )

    audio_files = []

    for blob in container_client.list_blobs():

        blob_name = blob.name

        if blob_name.lower().endswith(supported_extensions):
            audio_files.append(blob_name)

    return audio_files


def download_audio(blob_name, local_file):
    """
    Downloads an audio file from Azure Blob Storage
    to the local machine.
    """

    config = validate_config()
    blob_service_client = get_blob_service_client()

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

def transcribe_audio(audio_file):
    """
    Transcribes a WAV audio file using Azure Speech-to-Text.
    """

    import azure.cognitiveservices.speech as speechsdk

    config = validate_config()

    speech_config = speechsdk.SpeechConfig(
        subscription=config["speech_key"],
        region=config["speech_region"]
    )

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
        raise RuntimeError("Azure Speech could not recognize any speech.")

    elif result.reason == speechsdk.ResultReason.Canceled:

        cancellation = result.cancellation_details

        raise RuntimeError(
            f"Speech recognition canceled: "
            f"{cancellation.reason} - "
            f"{cancellation.error_details}"
        )

    else:
        raise RuntimeError(
            f"Unexpected Speech recognition result: {result.reason}"
        )

def upload_transcript(transcript_text, blob_name):
    """
    Uploads transcript text to the Azure transcripts container.
    """

    config = validate_config()
    blob_service_client = get_blob_service_client()

    container_client = blob_service_client.get_container_client(
        config["transcript_container"]
    )

    blob_client = container_client.get_blob_client(blob_name)

    blob_client.upload_blob(
        transcript_text,
        overwrite=True
    )

    return blob_name

def transcript_exists(blob_name):
    """
    Checks whether the transcript for an audio file
    already exists in the Azure transcripts container.
    """

    config = validate_config()
    blob_service_client = get_blob_service_client()

    container_client = blob_service_client.get_container_client(
        config["transcript_container"]
    )

    # Convert audio filename to transcript filename
    base_name = os.path.splitext(os.path.basename(blob_name))[0]
    transcript_blob = f"{base_name}.txt"

    blob_client = container_client.get_blob_client(transcript_blob)

    return blob_client.exists()

def process_all_audio_files():
    """
    Processes all supported audio files from the Azure audio container.
    """

    audio_files = list_audio_files()

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

            if transcript_exists(audio_file):
                print("   ⏭ Skipped (Transcript already exists)\n")
                skipped += 1
                continue

            process_audio_file(audio_file)

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

def process_audio_file(blob_name):
    """
    Processes one audio file from Azure Blob Storage.

    Steps:
    1. Download audio
    2. Convert to WAV
    3. Transcribe using Azure Speech
    4. Upload transcript
    5. Clean up temporary files
    """

    base_name = os.path.splitext(os.path.basename(blob_name))[0]

    local_audio = f"temp_input_{os.path.basename(blob_name)}"
    local_wav = f"temp_output_{base_name}.wav"

    try:
        print(f"\nProcessing: {blob_name}")

        # Step 1: Download original audio
        download_audio(blob_name, local_audio)
        print("  ✓ Audio downloaded")

        # Step 2: Convert to Speech-compatible WAV
        prepare_audio(local_audio, local_wav)
        print("  ✓ Audio converted")

        # Step 3: Transcribe audio
        transcript = transcribe_audio(local_wav)
        print("  ✓ Audio transcribed")

        # Step 4: Create transcript filename
        transcript_blob = f"{base_name}.txt"

        # Step 5: Upload transcript
        upload_transcript(transcript, transcript_blob)
        print(f"  ✓ Transcript uploaded: {transcript_blob}")

        return True

    finally:
        # Step 6: Always clean up temporary files
        cleanup(local_audio, local_wav)