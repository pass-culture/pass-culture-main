""" token """
import random

from utils.human_ids import humanize


def random_token(length=6):
    token = random.SystemRandom()
    return _tokenify([token.randint(1, 255) for index in range(length // 2)])


def _tokenify(indexes):
    return "".join([humanize(index) for index in indexes])
