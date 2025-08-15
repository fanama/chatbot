from youtube_transcript_api import YouTubeTranscriptApi
from html_to_markdown import convert_to_markdown

import urllib.request
import gzip

class Youtube:
    
    @staticmethod
    def generateText(url:str):
        print("URL : ",url)
        video_id = url.split("v=")[1]
        ytt_api = YouTubeTranscriptApi()
        fetched_transcript = ytt_api.fetch(video_id, languages=['fr', 'en'])

        text = ""

        # is iterable
        for snippet in fetched_transcript:
            text+=snippet.text
        return text
    
    @staticmethod
    def generateMArkdown(url:str):
        print("URL : ",url)
        req = urllib.request.Request(url, headers={'Accept-Encoding': 'gzip'})
        with urllib.request.urlopen(req) as response:
            raw = response.read()
            try:
                html = gzip.decompress(raw).decode("utf-8")
            except OSError:
                html = raw.decode("utf-8")

        markdown = convert_to_markdown(html)

        return markdown