import random
from typing import List

from .corpus import Corpus


class Seller:
    SEP = [
        '…', '…', '…', '…', '…', '…',
        '……', '……', '……', '……',
        '………', '………',
        '！', '！！',
        '、、', '、、、',
    ]
    MOAN = [
        '啊', '啊', '啊', '啊', '啊',
        '啊啊', '啊啊', '啊啊', '啊啊',
        '啊啊啊', '啊啊啊', '啊啊啊',
        '嗯', '嗯', '嗯', '嗯',
        '嗯嗯', '嗯嗯',
        '唔', '唔',
        '唔嗯', '唔嗯',
        '唔哇', '唔哇',
        '哇啊', '哇啊啊',
        '好舒服', '好棒', '继续', '用力', '不要停',
        '不要', '那里不可以', '好变态', '要坏掉啦',
    ]

    def __init__(self, corpus: Corpus):
        self.corpus = corpus

    def sell(self, keyword: str) -> List[str]:
        answers: List[str] = [sentence for sentence in self.corpus.common if
                              keyword in sentence] if keyword else self.corpus.common
        try:
            answers = sorted(random.sample(answers, 5))
        except ValueError:
            answers = sorted(answers[:5])
        return answers

    def vegetable_moan(self) -> str:
        def random_sep() -> str:
            return self.SEP[random.randint(0, len(self.SEP) - 1)]

        def random_text() -> str:
            text = self.MOAN[random.randint(0, len(self.MOAN) - 1)]
            while len(text) < 20 and (random.random() < 0.25):
                text += random_sep() + self.MOAN[random.randint(0, len(self.MOAN) - 1)]
            return text

        vegetable_count = random.randint(1, 3)
        vegetable_phrase_set = self.corpus.phrase[random.randint(0, 1)]
        vegetables = random.sample(vegetable_phrase_set, vegetable_count)

        text = ""
        for vegetable in vegetables:
            text += vegetable + random_sep() + random_text() + random_sep()

        return text
