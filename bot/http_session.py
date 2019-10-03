import aiohttp

from .bot import settings  # type: ignore


class HttpSession:
    _session = None
    _headers = {"Authorization": f"Token {settings.API_TOKEN}"}

    @classmethod
    def get_session(cls) -> aiohttp.ClientSession:
        if cls._session is None:
            cls._session = aiohttp.ClientSession(headers=cls._headers)
        return cls._session
