# Azure Speech-to-Text Pipeline

A cloud-native speech-to-text pipeline built with **Python, Azure Speech Service, Azure Blob Storage, Docker, Azure Container Registry, and Azure Container Apps**.

The application takes audio files stored in Azure Blob Storage, converts them into a Speech-compatible WAV format using FFmpeg, transcribes the audio using Azure Speech-to-Text, and stores the resulting transcript back in Azure Blob Storage.

---

## Architecture

```text
                Azure Blob Storage
                       │
                       │ Audio file
                       ▼
              Azure Container Apps
                       │
                       ▼
                Python Pipeline
                       │
                       ▼
                  FFmpeg
             Audio Conversion
                       │
                       ▼
             Azure Speech Service
                Speech-to-Text
                       │
                       ▼
                Transcript (.txt)
                       │
                       ▼
                Azure Blob Storage
                  transcripts/
```

---

## Features

* Upload audio files to Azure Blob Storage
* Supports multiple audio formats:

  * WAV
  * MP3
  * M4A
  * FLAC
  * OGG
  * WMA
  * AAC
* Automatic audio conversion using FFmpeg
* Azure Speech-to-Text transcription
* Stores generated transcripts in Azure Blob Storage
* Batch processing of multiple audio files
* Idempotent processing — existing transcripts are skipped
* Dockerized application
* Azure Container Registry deployment
* Azure Container Apps deployment
* Secure configuration using environment variables and Container App Secrets
* Temporary audio files are automatically cleaned up after processing

---

## Technology Stack

| Technology               | Purpose                          |
| ------------------------ | -------------------------------- |
| Python                   | Application and processing logic |
| Azure Blob Storage       | Audio and transcript storage     |
| Azure AI Speech          | Speech-to-text transcription     |
| FFmpeg                   | Audio format conversion          |
| Docker                   | Application containerization     |
| Azure Container Registry | Container image storage          |
| Azure Container Apps     | Cloud deployment                 |
| Azure CLI                | Azure resource management        |

---

## Project Structure

```text
azure-speech-to-text-pipeline/
│
├── app.py
├── api.py
├── speech_pipeline.py
├── config.py
├── utils.py
│
├── Dockerfile
├── requirements.txt
├── .dockerignore
├── .gitignore
├── .env.example
└── README.md
```

### File Responsibilities

**`app.py`**

Application entry point. Validates configuration and starts batch processing.

**`speech_pipeline.py`**

Contains the core pipeline:

```text
List audio files
      ↓
Check transcript
      ↓
Download audio
      ↓
Convert audio
      ↓
Transcribe
      ↓
Upload transcript
      ↓
Cleanup
```

**`config.py`**

Loads and validates environment variables.

**`utils.py`**

Contains utility functions such as FFmpeg audio conversion and temporary-file cleanup.

**`api.py`**

Contains the FastAPI implementation for the API-based version of the application.

---

## How the Pipeline Works

### 1. Audio Upload

Audio files are placed inside the Azure Blob Storage:

```text
audio/
```

Example:

```text
audio/
├── sample.wav
├── sample2.wav
└── test.ogg
```

---

### 2. Audio Discovery

The application scans the `audio` container and identifies supported audio formats.

---

### 3. Transcript Check

Before processing an audio file, the application checks whether a corresponding transcript already exists.

For example:

```text
audio/sample.wav
```

checks for:

```text
transcripts/sample.txt
```

If the transcript already exists, the file is skipped.

This makes the pipeline **idempotent** and avoids unnecessary processing and Azure Speech API calls.

---

### 4. Audio Download

The audio file is downloaded temporarily from Azure Blob Storage.

---

### 5. Audio Conversion

FFmpeg converts the source audio into a Speech-compatible WAV format:

```text
Mono
16 kHz
16-bit PCM
```

This allows the pipeline to process multiple audio formats consistently.

---

### 6. Speech-to-Text

The converted audio is sent to Azure Speech Service.

The recognized text is returned by the Speech SDK.

---

### 7. Transcript Upload

The transcript is uploaded back to Azure Blob Storage:

```text
transcripts/
```

For example:

```text
sample.txt
```

---

### 8. Cleanup

Temporary downloaded and converted files are deleted after processing.

---

## Batch Processing

The pipeline can process multiple audio files in one execution.

Example output:

```text
=========================================
 Batch Processing
=========================================
Found 3 supported audio file(s).

[1/3] sample.wav
   ⏭ Skipped (Transcript already exists)

[2/3] sample2.wav

Processing: sample2.wav
  ✓ Audio downloaded
  ✓ Audio converted
  ✓ Audio transcribed
  ✓ Transcript uploaded: sample2.txt

[3/3] test.ogg

Processing: test.ogg
  ✓ Audio downloaded
  ✓ Audio converted
  ✓ Audio transcribed
  ✓ Transcript uploaded: test.txt

=========================================
 Batch Summary
=========================================
Processed : 2
Skipped   : 1
Failed    : 0
=========================================
```

---

## Local Setup

### Prerequisites

Install:

* Python 3.12+
* Docker
* FFmpeg
* Azure CLI
* An Azure subscription
* Azure Speech Service
* Azure Storage Account

---

### Clone the Repository

```bash
git clone https://github.com/Yashdub1045/azure-speech-to-text-pipeline.git
cd azure-speech-to-text-pipeline
```

---

### Create Virtual Environment

Windows PowerShell:

```powershell
python -m venv venv
```

Activate:

```powershell
.\venv\Scripts\Activate.ps1
```

---

### Install Dependencies

```powershell
pip install -r requirements.txt
```

---

### Configure Environment Variables

Create a `.env` file based on:

```text
.env.example
```

Example:

```text
SPEECH_KEY=your_speech_key
SPEECH_REGION=your_region
STORAGE_CONNECTION_STRING=your_storage_connection_string
STORAGE_CONTAINER=audio
TRANSCRIPT_CONTAINER=transcripts
```

**Never commit `.env` to GitHub.**

---

## Run Locally

```powershell
python app.py
```

The application will connect to Azure Blob Storage, process available audio files, call Azure Speech Service, and upload the generated transcripts.

---

## Docker

### Build the Image

```powershell
docker build -t speech-pipeline:v1 .
```

### Run the Container

```powershell
docker run --name speech-container --env-file .env speech-pipeline:v1
```

---

## Azure Deployment

The application is deployed using:

```text
Azure Container Registry
          │
          ▼
Azure Container Apps
```

The Docker image is stored in Azure Container Registry.

Example:

```text
rgsprodreg.azurecr.io/speech-pipeline:v1
```

The container runs inside an Azure Container Apps environment.

Azure Container App Secrets are used for sensitive configuration such as:

```text
SPEECH_KEY
STORAGE_CONNECTION_STRING
```

Secrets are referenced by the application rather than being embedded inside the Docker image.

---

## Azure Resources

The V1 deployment uses the following Azure services:

```text
Resource Group
│
├── Azure Storage Account
│   ├── audio
│   └── transcripts
│
├── Azure AI Speech Service
│
├── Azure Container Registry
│
└── Azure Container Apps
    └── speech-pipeline
```

---

## Security

Sensitive configuration is intentionally excluded from source control.

The following files and directories are ignored:

```text
.env
venv/
__pycache__/
*.pyc
```

The repository contains `.env.example` with placeholder values so that users can understand the required configuration without exposing credentials.

---

## Current Version

### V1 — Batch Processing

Current architecture:

```text
Blob Storage
     │
     ▼
Container Apps
     │
     ▼
Python Pipeline
     │
     ├── FFmpeg
     │
     ▼
Azure Speech
     │
     ▼
Blob Storage
```

The current version uses batch processing and checks existing transcripts before processing.

---

## Future Improvements

### V2 — Event-Driven Architecture

The next version will move from polling/batch processing toward an event-driven architecture:

```text
Azure Blob Storage
        │
        │ BlobCreated
        ▼
    Event Grid
        │
        ▼
Container App Job
        │
        ▼
Python Speech Pipeline
        │
        ▼
 Azure Speech
        │
        ▼
Blob Storage
```

Planned improvements include:

* Azure Event Grid integration
* Container Apps Jobs
* Event-driven audio processing
* Better scalability
* FastAPI-based API interface
* GitHub Actions CI/CD
* Improved monitoring and logging

---

## Learning Objectives

This project demonstrates practical experience with:

* Azure cloud services
* Azure Blob Storage
* Azure AI Speech
* Docker containerization
* Container image management
* Azure Container Registry
* Azure Container Apps
* Azure CLI
* Secrets management
* Event-driven cloud architecture
* Python application development
* Basic cloud-native design

---

## Author

**Yash Dubey**

GitHub:
https://github.com/Yashdub1045

---

## License

This project is available for learning and portfolio purposes.
