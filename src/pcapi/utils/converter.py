from typing import List


def from_tuple_to_int(offer_ids: List[tuple]) -> List[int]:
    return [offer[0] for offer in offer_ids]