import random
from dataclasses import dataclass, field
from typing import List

from httpx import AsyncClient, NetworkError, HTTPError
from httpcore import TimeoutException

BASE_URL = "https://raw.githubusercontent.com/Chi-Task-Force/Chi-Corpus/master"


class UpdateException(Exception):
    pass


@dataclass
class Corpus:
    common: List[str] = field(default_factory=list)
    refuse: List[str] = field(default_factory=list)
    trigger: List[str] = field(default_factory=list)
    phrase: List[List[str]] = field(default_factory=list)

    def __post_init__(self):
        self.http = AsyncClient()

    async def update(self):
        try:
            self.common = (await self.http.get(f"{BASE_URL}/common.txt")).text.strip().split("\n")
            self.refuse = (await self.http.get(f"{BASE_URL}/refuse.txt")).text.strip().split("\n")
            self.trigger = (await self.http.get(f"{BASE_URL}/trigger.txt")).text.strip().split("\n")
            self.phrase = [item.split(" ") for item in (await self.http.get(f"{BASE_URL}/phrase.txt")).text.strip().split("\n")]
        except (NetworkError, HTTPError, TimeoutException) as e:
            raise UpdateException from e

    def get_rnd_common(self):
        return self.common[random.randint(0, len(self.common) - 1)]

    def get_rnd_refuse(self):
        return self.refuse[random.randint(0, len(self.refuse) - 1)]
