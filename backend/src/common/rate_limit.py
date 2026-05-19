from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address


def _key_func(request: Request) -> str:
    return get_remote_address(request)


limiter = Limiter(key_func=_key_func)
