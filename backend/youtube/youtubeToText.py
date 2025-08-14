from youtube_transcript_api import YouTubeTranscriptApi

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