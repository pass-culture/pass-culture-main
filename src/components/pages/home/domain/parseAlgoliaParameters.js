export const CONTENTFUL_PARAMETERS = {
  AROUND_RADIUS: 'aroundRadius',
  BEGINNING_DATETIME: 'beginningDatetime',
  CATEGORIES: 'categories',
  ENDING_DATETIME: 'endingDatetime',
  HITS_PER_PAGE: 'hitsPerPage',
  IS_DIGITAL: 'isDigital',
  IS_DUO: 'isDuo',
  IS_EVENT: 'isEvent',
  IS_FREE: 'isFree',
  IS_GEOLOCATED: 'isGeolocated',
  IS_THING: 'isThing',
  NEWEST_ONLY: 'newestOnly',
  PRICE_MAX: 'priceMax',
  PRICE_MIN: 'priceMin',
  TAGS: 'tags',
}

export const parseAlgoliaParameters = ({ geolocation, parameters }) => {
  const aroundRadius = parameters[CONTENTFUL_PARAMETERS.AROUND_RADIUS]
  const isGeolocated = parameters[CONTENTFUL_PARAMETERS.IS_GEOLOCATED]
  const priceMin = parameters[CONTENTFUL_PARAMETERS.PRICE_MIN]
  const priceMax = parameters[CONTENTFUL_PARAMETERS.PRICE_MAX]

  const notGeolocatedButRadiusIsProvided = !isGeolocated && aroundRadius
  const geolocatedButGeolocationIsInvalid = isGeolocated && !geolocation.latitude && !geolocation.longitude

  if (notGeolocatedButRadiusIsProvided || geolocatedButGeolocationIsInvalid) {
    return null
  }

  const beginningDatetime = parameters[CONTENTFUL_PARAMETERS.BEGINNING_DATETIME] ? new Date(parameters[CONTENTFUL_PARAMETERS.BEGINNING_DATETIME]) : null
  const endingDatetime = parameters[CONTENTFUL_PARAMETERS.ENDING_DATETIME] ? new Date(parameters[CONTENTFUL_PARAMETERS.ENDING_DATETIME]) : null

  return {
    aroundRadius: aroundRadius || null,
    beginningDatetime: beginningDatetime,
    endingDatetime: endingDatetime,
    geolocation: geolocation || null,
    hitsPerPage: parameters[CONTENTFUL_PARAMETERS.HITS_PER_PAGE] || null,
    offerCategories: parameters[CONTENTFUL_PARAMETERS.CATEGORIES] || [],
    offerIsDuo: parameters[CONTENTFUL_PARAMETERS.IS_DUO] || false,
    offerIsFree: parameters[CONTENTFUL_PARAMETERS.IS_FREE] || false,
    offerIsNew: parameters[CONTENTFUL_PARAMETERS.NEWEST_ONLY] || false,
    offerTypes: {
      isDigital: parameters[CONTENTFUL_PARAMETERS.IS_DIGITAL] || false,
      isEvent: parameters[CONTENTFUL_PARAMETERS.IS_EVENT] || false,
      isThing: parameters[CONTENTFUL_PARAMETERS.IS_THING] || false,
    },
    priceRange: buildPriceRange({ priceMin, priceMax }),
    searchAround: parameters[CONTENTFUL_PARAMETERS.IS_GEOLOCATED] || false,
    tags: parameters[CONTENTFUL_PARAMETERS.TAGS] || [],
  }
}

const buildPriceRange = ({ priceMin = 0, priceMax = 500 }) => {
  return [priceMin, priceMax]
}
