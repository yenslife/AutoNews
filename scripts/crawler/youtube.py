import json

import requests
from rich import print
import yt_dlp

# TODO: 判斷該影片有沒有字幕，如果沒有字幕，使用 Whisper API 進行語音辨識，可能會需要先將音源下載下來
# TODO: 判斷某些頻道有沒有新影片，如果有就要下載字幕


def get_youtube_transcript(
    video_id: str, languages: list[str] = ["zh-TW", "zh-Hant", "en", "zh-Hans"]
) -> str | None:
    ydl_opts = {
        "writesubtitles": True,
        "subtitlesformat": "srt",
        "skip_download": True,  # 跳過下載影片
    }
    url = f"https://www.youtube.com/watch?v={video_id}"
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        with open("info.json", "w", encoding="utf-8") as f:
            json.dump(info, f, ensure_ascii=False, indent=4)
        if info is None:
            print(f"無法擷取影片 {video_id} 的資訊。")
            return None
        if not info.get("subtitles"):
            print(f"在影片 {video_id} 中找不到字幕。")
            return None

        print(
            f"這個影片有這些字幕：{[k for k, _ in info.get('subtitles', {}).items()]}"
        )

        selected_lang = None
        for lang in languages:
            if lang in info.get("subtitles", {}):
                selected_lang = lang
                print(
                    f"使用 {lang} 作為 id {video_id}，影片「{info.get('title', '無標題')}」的語言"
                )
                break
            else:
                print(f"在影片 {video_id} 中找不到 {lang} 的字幕")

        if selected_lang is None:
            print(f"在影片 {video_id} 中找不到任何指定語言的字幕")
            return None

        # 取得字幕 URL
        subtitle_info = info.get("subtitles", {}).get(selected_lang)
        if not subtitle_info or len(subtitle_info) == 0:
            print(f"無法取得 {selected_lang} 字幕的詳細資訊")
            return None

        subtitle_url = ""
        for subtitle_type in subtitle_info:
            if subtitle_type.get("ext") == "srt":
                subtitle_url = subtitle_type.get("url")
                break

        if not subtitle_url:
            print(f"無法取得 {selected_lang} 字幕的 URL")
            return None

        # 下載字幕內容
        try:
            response = requests.get(subtitle_url)
            response.raise_for_status()  # 確保請求成功
            return response.text
        except requests.RequestException as e:
            print(f"下載字幕內容時發生錯誤: {e}")
            return None


def get_transcript(
    video_id: str, languages: list[str] = ["zh-TW", "zh-Hant", "en", "zh-Hans"]
) -> str | None:
    # TODO: 將 get_youtube_transcript 和 whisper_api 的功能合併，如果沒有 yt_dlp 的字幕，就使用 whisper_api 進行語音辨識
    pass


def get_youtube_audio(video_id: str):
    url = f"https://www.youtube.com/watch?v={video_id}"
    ydl_opts = {
        "format": "m4a/bestaudio/best",
        # ℹ️ See help(yt_dlp.postprocessor) for a list of available Postprocessors and their arguments
        "postprocessors": [
            {  # Extract audio using ffmpeg
                "key": "FFmpegExtractAudio",
                "preferredcodec": "m4a",
            }
        ],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        if not info:
            print(f"無法擷取影片 {video_id} 的資訊。")
            return None
        print(f"Downloaded audio for video {video_id}: {info['title']}")

    # return binary audio data
    return ydl.prepare_filename(info)


def get_youtube_thumbnail(video_id: str) -> str | None:
    """
    成功下載會回傳縮圖檔案名稱
    """
    url = f"https://www.youtube.com/watch?v={video_id}"
    ydl_opts = {
        "skip_download": True,  # Skip downloading the video
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        if not info:
            print(f"無法擷取影片 {video_id} 的資訊。")
            return None
        url = info.get("thumbnail", None)
        if not url:
            print(f"無法取得影片 {video_id} 的縮圖。")
            return None
        print(f"Thumbnail URL for video {video_id}: {url}")

        try:
            response = requests.get(url)
        except requests.RequestException as e:
            print(f"下載縮圖時發生錯誤: {e}")
            return None

        with open(f"{video_id}_thumbnail.jpg", "wb") as f:
            f.write(response.content)

        return f"{video_id}_thumbnail.jpg"


if __name__ == "__main__":
    ytt_id = "AVIKFXLCPY8"
    ytt_id = "HnzDaEiN_eg"
    # ytt_id = 'YFQUZ08hYaQ'
    # ytt_id = '18R_RORjvUU'
    # ytt_id = "FWAdfuPpLOc"  # 多語言的字幕 只有簡體中文
    # ytt_id = "0e3GPea1Tyg"  # 多語言的字幕 有繁體中文

    ## test for get_youtube_audio
    result = get_youtube_audio(ytt_id)
    print("下載的音訊檔:", result)

    ## test for get_youtube_transcript
    result = get_youtube_transcript(ytt_id)
    print("找到的 srt:", result)

    ## test for get_youtube_thumbnail
    result = get_youtube_thumbnail(ytt_id)
    print("找到的縮圖: ", result)
