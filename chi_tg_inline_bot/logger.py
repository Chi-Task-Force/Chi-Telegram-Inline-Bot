import json
import os
from asyncio import Lock

import aiofiles


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


    async def log(self, sentence, user):
        async with self.lock:
            self.data["total"] += 1
            self.data["per_sentence"][sentence] = self.data["per_sentence"].get(sentence, 0) + 1
            self.data["per_user"][user] = self.data["per_user"].get(user, 0) + 1
            async with aiofiles.open(self.filename, mode="w") as f:
                await f.write(json.dumps(self.data, ensure_ascii=False))
