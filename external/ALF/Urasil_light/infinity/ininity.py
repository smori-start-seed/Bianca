from dataclasses import dataclass
from typing import List


@dataclass
class IninityFragment:
    tag: str
    payload: str


class IninityLog:
    def __init__(self):
        self.fragments: List[IninityFragment] = []

    def append(self, tag: str, payload: str) -> None:
        self.fragments.append(IninityFragment(tag=tag, payload=payload))

    def last_n(self, n: int) -> List[IninityFragment]:
        return self.fragments[-n:]
