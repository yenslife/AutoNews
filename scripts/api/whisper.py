import os
import requests
from dotenv import load_dotenv
from rich import print

load_dotenv()
base_url = os.getenv("WHISPER_API_BASE_URL")
print("base_url", base_url)


def transcribe_audio(file_path: str) -> str:

    if not base_url:
        raise ValueError("WHISPER_API_BASE_URL environment variable is not set.")

    files = {"audio_file": open(file_path, "rb")}
    data = {
        "model_size": "large-v3",
    }
    transcript_url = base_url + "/get-transcript"
    print("發送請求到", transcript_url)
    response = requests.post(transcript_url, files=files, data=data)

    if response.status_code != 200:
        raise Exception(f"Error: {response.status_code} - {response.text}")

    response_json = response.json()
    print("音訊轉換結果:", response_json)

    return response_json.get("text", "")


if __name__ == "__main__":
    # Example usage
    try:
        transcription = transcribe_audio("/Users/mac/Downloads/test.m4a")
        print("Transcription:", transcription)

    except Exception as e:
        print("An error occurred:", str(e))
