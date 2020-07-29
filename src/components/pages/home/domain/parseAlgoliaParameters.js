const algoliaParametersFromContentful = {
  AROUND_RADIUS: 'aroundRadius',
  BEGINNING_DATETIME: 'beginningDatetime',
  CATEGORIES: 'categories',
  ENDING_DATETIME: 'endingDatetime',
  HITS_PER_PAGE: 'hitsPerPage',
  IS_DIGITAL: 'isDigital',
  IS_DUO: 'isDuo',
  IS_EVENT: 'isEvent',
  IS_GEOLOCATED: 'isGeolocated',
  IS_THING: 'isThing',
  NEWEST_ONLY: 'newestOnly',
  PRICE_MAX: 'priceMax',
  PRICE_MIN: 'priceMin',
  TAGS: 'tags',
}

export const parseAlgoliaParameters = parameters => {
  const priceMin = parameters[algoliaParametersFromContentful.PRICE_MIN]
  const priceMax = parameters[algoliaParametersFromContentful.PRICE_MAX]
  return ({
    hitsPerPage: parameters[algoliaParametersFromContentful.HITS_PER_PAGE] || null,
    offerCategories: parameters[algoliaParametersFromContentful.CATEGORIES] || [],
    offerIsDuo: parameters[algoliaParametersFromContentful.IS_DUO] || false,
    offerIsNew: parameters[algoliaParametersFromContentful.NEWEST_ONLY] || false,
    offerTypes: {
      isDigital: parameters[algoliaParametersFromContentful.IS_DIGITAL] || false,
      isEvent: parameters[algoliaParametersFromContentful.IS_EVENT] || false,
      isThing: parameters[algoliaParametersFromContentful.IS_THING] || false,
    },
    priceRange: !priceMin && !priceMax ? [] : buildPriceRange({ priceMin, priceMax }),
    tags: parameters[algoliaParametersFromContentful.TAGS] || [],
  })
}

const buildPriceRange = ({ priceMin = 0, priceMax = 500 }) => {
  return [priceMin, priceMax]
}
