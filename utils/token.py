import itertools
import random

from utils.human_ids import humanize

def tokenify(indexes):
    return  "".join([humanize(index) for index in indexes])

def random_token(length = 3):
    token = random.SystemRandom()
    return tokenify([token.randint(1, 256) for index in range(length)])

def get_all_tokens(length = 3):
    return map(tokenify,
               itertools.product(*[range(1, 256) for index in range(length)]))
