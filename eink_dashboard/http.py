import ssl
import urllib.request


def fetch_bytes(url: str, user_agent: str, timeout: int = 6) -> bytes:
    context = ssl.create_default_context()
    request = urllib.request.Request(url, headers={"User-Agent": user_agent})
    with urllib.request.urlopen(request, timeout=timeout, context=context) as response:
        return response.read()

