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
  let parsedParameters = {}
  const keys = Object.keys(parameters)

  keys.forEach(key => {
    switch (key) {
      case algoliaParametersFromContentful.CATEGORIES:
        parsedParameters['offerCategories'] = parameters[key]
        break
      case algoliaParametersFromContentful.IS_DUO:
        parsedParameters['offerIsDuo'] = parameters[key]
        break
      case algoliaParametersFromContentful.HITS_PER_PAGE:
        parsedParameters['hitsPerPage'] = parameters[key]
        break
      case algoliaParametersFromContentful.NEWEST_ONLY:
        parsedParameters['offerIsNew'] = parameters[key]
        break
      case algoliaParametersFromContentful.TAGS:
        parsedParameters['tags'] = parameters[key]
        break
    }
  })
  return parsedParameters
}
