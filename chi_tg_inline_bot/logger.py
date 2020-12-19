import json
import os
from dataclasses import dataclass
from asyncio import Lock
from typing import Dict, Optional

import aiofiles

@dataclass
class Stat:
    total_requests: int
    users: int
    top_sentences: Dict[str, int]
    top_user_count: int

class InlineLogger:
    def __init__(self, filename: str):
        self.lock = Lock()
        self.filename = filename
        self.data = {}
        if os.path.exists(self.filename):
            try:
                with open(self.filename) as f:
                    self.data = json.load(f)
            except json.JSONDecodeError:
                pass
        if not self.data:
            self.data = {"total": 0, "per_sentence": {}, "per_user": {}}

    async def log(self, sentence: str, user: str):
        async with self.lock:
            self.data["total"] += 1
            self.data["per_sentence"][sentence] = self.data["per_sentence"].get(sentence, 0) + 1
            self.data["per_user"][user] = self.data["per_user"].get(user, 0) + 1
            async with aiofiles.open(self.filename, mode="w") as f:
                await f.write(json.dumps(self.data, ensure_ascii=False))

    async def get_user_stat(self, user: str) -> Optional[int]:
        return self.data["per_user"].get(user)

    async def get_stat(self) -> Stat:
        top_sentences = {(k if k != "-1" else "菜喘"):v for k, v in sorted(self.data["per_sentence"].items(), key=lambda x: x[1], reverse=True)[:5]}
        per_user_iter = self.data["per_user"].items()
        return Stat(self.data["total"], len(self.data["per_user"]), top_sentences, max(per_user_iter, key=lambda x: x[1])[1])
