from urllib.parse import urlparse

ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
BASE = len(ALPHABET)


def encode_base62(num: int) -> str:
    if num < 0:
        raise ValueError("Number must be non-negative")
    if num == 0:
        return ALPHABET[0]

    chars = []
    while num > 0:
        num, rem = divmod(num, BASE)
        chars.append(ALPHABET[rem])
    return "".join(reversed(chars))


def is_valid_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except ValueError:
        return False