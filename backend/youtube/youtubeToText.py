import gzip
import logging
import urllib.request
from urllib.parse import parse_qs, urlparse

from html_to_markdown import convert_to_markdown
from youtube_transcript_api import YouTubeTranscriptApi

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT = 10
# Refuse to buffer an unbounded response body in memory.
MAX_CONTENT_BYTES = 5 * 1024 * 1024


def extract_youtube_id(url: str) -> str:
    """Extract the video id from any YouTube URL form.

    The previous `url.split("v=")[1]` raised IndexError on `youtu.be/...`,
    `/shorts/...`, `/embed/...` and on any URL without a `v=` parameter.
    """
    parsed = urlparse(url)
    host = parsed.netloc.lower()

    if host.endswith("youtu.be"):
        candidate = parsed.path.lstrip("/")
        if candidate:
            return candidate.split("/")[0]

    values = parse_qs(parsed.query).get("v")
    if values and values[0]:
        return values[0]

    for prefix in ("/embed/", "/shorts/", "/live/", "/v/"):
        if parsed.path.startswith(prefix):
            candidate = parsed.path[len(prefix):].split("/")[0]
            if candidate:
                return candidate

    raise ValueError(f"Could not extract a YouTube video id from: {url}")


_instance: "Youtube | None" = None


def get_transcript() -> "Youtube":
    """Return the shared helper, created on first use.

    The `/query` route and the `query_collection_tool` tool both need it and
    each used to keep its own duplicate singleton.
    """
    global _instance
    if _instance is None:
        _instance = Youtube()
    return _instance


class Youtube:

    @staticmethod
    def generateText(url: str) -> str:
        logger.info("Fetching transcript for %s", url)
        try:
            video_id = extract_youtube_id(url)
            fetched_transcript = YouTubeTranscriptApi().fetch(
                video_id, languages=['fr', 'en']
            )
        except Exception:
            logger.warning("Transcript unavailable for %s", url, exc_info=True)
            return ""

        return "".join(snippet.text for snippet in fetched_transcript)

    @staticmethod
    def generateMArkdown(url: str) -> str:
        logger.info("Fetching page content for %s", url)
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            raise ValueError(f"Unsupported URL scheme: {parsed.scheme!r}")

        req = urllib.request.Request(
            url, headers={'Accept-Encoding': 'gzip', 'User-Agent': 'Mozilla/5.0'}
        )
        # urlopen had no timeout: a slow host pinned the worker thread forever.
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as response:
            raw = response.read(MAX_CONTENT_BYTES)
            encoding = response.headers.get("Content-Encoding", "")

        if encoding == "gzip" or raw[:2] == b"\x1f\x8b":
            try:
                html = gzip.decompress(raw).decode("utf-8", errors="replace")
            except OSError:
                html = raw.decode("utf-8", errors="replace")
        else:
            html = raw.decode("utf-8", errors="replace")

        return convert_to_markdown(html)
