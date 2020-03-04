from typing import List

from models import IrisFrance

# TODO : compare venue distance to iris (<100km)

def find_iris_near_venue(venueId: int) -> List:
    iris_france = IrisFrance.query.all()
    iris_ids = [iris.id for iris in iris_france]
    return iris_ids
