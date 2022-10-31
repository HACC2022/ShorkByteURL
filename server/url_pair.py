from typing import Optional
from random import randrange

def generate_random_string() -> str:
    return str(randrange(0, int(1e6)))

class URLPair:
    orig_url: str
    short_url: str

    def __init__(self,orig_url: str, short_url:Optional[str]=None) -> None:
        self.orig_url = orig_url
        self.short_url = short_url if short_url is not None else generate_random_string()
        if not self.short_url.startswith("/"): self.short_url = "/" + self.short_url
    
    def regenerate(self) -> None:
        self.short_url = generate_random_string()