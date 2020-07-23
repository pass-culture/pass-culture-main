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
  TAGS: 'tags'
}

export const parseAlgoliaParameters = parameters => {
  let parsedParameters = {}
  const keys = Object.keys(parameters)

  keys.forEach(key => {
    switch (key) {
      case algoliaParametersFromContentful.CATEGORIES:
        if (parameters[key].length > 0) {
          parsedParameters['offerCategories'] = parameters[key]
        }
        break
      case algoliaParametersFromContentful.TAGS:
        if (parameters[key].length > 0) {
          parsedParameters['tags'] = parameters[key]
        }
        break
    }
  })
  return parsedParameters
}
