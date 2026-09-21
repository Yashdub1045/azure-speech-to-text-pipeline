import os
import subprocess


def convert_to_wav(input_file, output_file):
    """
    Converts an audio file to a Speech-compatible WAV file.

    Output:
    - Mono audio
    - 16 kHz sample rate
    - 16-bit PCM
    """

    command = [
        "ffmpeg",
        "-y",
        "-i",
        input_file,
        "-ac",
        "1",
        "-ar",
        "16000",
        "-sample_fmt",
        "s16",
        output_file,
    ]

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"FFmpeg conversion failed:\n{result.stderr}"
        )


def cleanup(*files):
    """
    Deletes temporary files if they exist.
    """

    for file in files:

        if file and os.path.exists(file):
            os.remove(file)