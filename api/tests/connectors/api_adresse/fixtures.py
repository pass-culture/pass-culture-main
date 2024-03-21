ONE_FEATURE_RESPONSE = {
    "type": "FeatureCollection",
    "version": "draft",
    "features": [
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [2.338562, 48.890787]},
            "properties": {
                "label": "18 Rue Duhesme 75018 Paris",
                "score": 0.9806027272727271,
                "housenumber": "18",
                "id": "75118_2974_00018",
                "name": "18 Rue Duhesme",
                "postcode": "75018",
                "citycode": "75118",
                "x": 651500.23,
                "y": 6865844.9,
                "city": "Paris",
                "district": "Paris 18e Arrondissement",
                "context": "75, Paris, Île-de-France",
                "type": "housenumber",
                "importance": 0.78663,
                "street": "Rue Duhesme",
            },
        }
    ],
    "attribution": "BAN",
    "licence": "ETALAB-2.0",
    "query": "18 rue Duhesme",
    "filters": {"citycode": "75118"},
    "limit": 1,
}

NO_FEATURE_RESPONSE = {
    "type": "FeatureCollection",
    "version": "draft",
    "features": [],
    "attribution": "BAN",
    "licence": "ETALAB-2.0",
    "query": "123456789",
    "filters": {"citycode": "75118"},
    "limit": 1,
}

MUNICIPALITY_CENTROID_RESPONSE = {
    "type": "FeatureCollection",
    "version": "draft",
    "features": [
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [2.348679, 48.892045]},
            "properties": {
                "label": "Paris 18e Arrondissement",
                "score": 0.2084164031620553,
                "id": "75118",
                "type": "municipality",
                "name": "Paris 18e Arrondissement",
                "postcode": "75018",
                "citycode": "75118",
                "x": 652243.19,
                "y": 6865978.62,
                "population": 192468,
                "city": "Paris 18e Arrondissement",
                "context": "75, Paris, Île-de-France",
                "importance": 0.55345,
                "municipality": "Paris 18e Arrondissement",
            },
        }
    ],
    "attribution": "BAN",
    "licence": "ETALAB-2.0",
    "query": "Paris",
    "filters": {"citycode": "75118", "type": "municipality"},
    "limit": 1,
}

SEARCH_CSV_HEADERS = [
    "venue_id",
    "venue_ban_id",
    "q",
    "latitude",
    "longitude",
    "result_id",
    "result_label",
    "result_score",
]
SEARCH_CSV_RESULTS = [
    # Matching ban_id:
    {
        "venue_id": 1,
        "venue_ban_id": "38185_1660_00033",
        "q": "33 Boulevard Clemenceau Grenoble",
        "latitude": 45.18403,
        "longitude": 5.740288,
        "result_id": "38185_1660_00033",
        "result_label": "33 Boulevard Clemenceau 38100 Grenoble",
        "result_score": 0.9762045454545454,
    },
    # Mismatching ban_id / Wrong ban_id / Housenumber / Fixable:
    {
        "venue_id": 2,
        "venue_ban_id": "38185_3000_00033",
        "q": "33 Boulevard Clemenceau Grenoble",
        "latitude": 45.18403,
        "longitude": 5.740288,
        "result_id": "38185_1660_00033",
        "result_label": "33 Boulevard Clemenceau 38100 Grenoble",
        "result_score": 0.9762045454545454,
    },
    # Mismatching ban_id / Missing ban_id / Housenumber / Fixable:
    {
        "venue_id": 3,
        "venue_ban_id": None,
        "q": "33 Boulevard Clemenceau Grenoble",
        "latitude": 45.18403,
        "longitude": 5.740288,
        "result_id": "38185_1660_00033",
        "result_label": "33 Boulevard Clemenceau 38100 Grenoble",
        "result_score": 0.9762045454545454,
    },
    # Mismatching ban_id / Wrong ban_id / Street / Fixable:
    {
        "venue_id": 4,
        "venue_ban_id": "38185_3000_00033",
        "q": "Boulevard Clemenceau Grenoble",
        "latitude": 45.183808,
        "longitude": 5.739678,
        "result_id": "38185_1660",
        "result_label": "Boulevard Clemenceau 38100 Grenoble",
        "result_score": 0.9762045454545454,
    },
    # Mismatching ban_id / Missing ban_id / Street / Non-fixable:
    {
        "venue_id": 5,
        "venue_ban_id": None,
        "q": "This address does not exist",
        "latitude": 48.644701,
        "longitude": -3.898144,
        "result_id": "29023_2455",
        "result_label": "Rue des Hauts de Ty Nod 29660 Carantec",
        "result_score": 0.17157103896103892,
    },
]
