from rich import print
from youtube_transcript_api import YouTubeTranscriptApi # type: ignore[reportMissingExports]
from youtube_transcript_api import TranscriptsDisabled # type: ignore[reportMissingImports]

# TODO: 判斷該影片有沒有字幕，如果沒有字幕，使用 Whisper API 進行語音辨識，可能會需要先將音源下載下來
# TODO: 判斷某些頻道有沒有新影片，如果有就要下載字幕
ytt_id = 'AVIKFXLCPY8'
ytt_id = 'HnzDaEiN_eg'
ytt_id = 'YFQUZ08hYaQ'
# ytt_id = '18R_RORjvUU'
ytt_api = YouTubeTranscriptApi()
result = None
try:
    result = ytt_api.fetch(video_id=ytt_id, languages=['en', 'zh-TW'])
except TranscriptsDisabled as e:
    print("此影片沒有字幕，請使用 Whisper API 進行語音辨識")

print(result)

