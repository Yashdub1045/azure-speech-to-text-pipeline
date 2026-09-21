from config import validate_config
from speech_pipeline import process_all_audio_files


def main():
    """
    Main entry point of the Azure Speech-to-Text application.
    """

    print("======================================")
    print(" Azure Speech-to-Text Pipeline")
    print("======================================")

    # Validate configuration before starting
    validate_config()

    # Process all available audio files
    process_all_audio_files()


if __name__ == "__main__":
    main()