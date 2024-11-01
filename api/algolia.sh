#! /bin/sh

if [ ! "$ALGOLIA_API_KEY" ] || [ ! "$ALGOLIA_APP_ID" ]; then
    echo "Error: environment variables ALGOLIA_API_KEY and ALGOLIA_APP_ID are not set" 1>&2
    exit 1
fi

index="PRODUCTION B"
query="jamais plus"
subcategory="LIVRE_PAPIER"
nb_results=2
data=$(
    cat <<EOM
{
    "requests": [
        {
            "indexName": "$index",
            "query": "\"$query\"",
            "advancedSyntax": true,
            "params": "page=0&hitsPerPage=$nb_results",
            "aroundRadius": "1000000",
            "aroundLatLng": "48.87171, 2.308289",
            "facetFilters": [["offer.subcategoryId:$subcategory"]],
            "attributesToRetrieve": [
                "distinct",
                "objectID",
                "offer.indexedAt",
                "offer.last30DaysBookings",
                "offer.name"
            ],
            "distinct": false
        }
    ]
}
EOM
)

curl "https://e2ikxj325n-dsn.algolia.net/1/indexes/*/queries" \
    -H "x-algolia-api-key: $ALGOLIA_API_KEY" \
    -H "x-algolia-application-id: $ALGOLIA_APP_ID" \
    -d "$data" \
    2>/dev/null |
    jq -r -f algolia_hit_to_csv.jq
