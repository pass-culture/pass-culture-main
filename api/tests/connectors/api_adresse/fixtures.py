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
