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
  const parsedParameters = {}
  const offerTypes ={
    isDigital: false,
    isEvent: false,
    isThing: false,
  }
  const keys = Object.keys(parameters)

  keys.forEach(key => {
    const value = parameters[key]
    switch (key) {
      case algoliaParametersFromContentful.CATEGORIES:
        parsedParameters['offerCategories'] = value
        break
      case algoliaParametersFromContentful.IS_DUO:
        parsedParameters['offerIsDuo'] = value
        break
      case algoliaParametersFromContentful.HITS_PER_PAGE:
        parsedParameters['hitsPerPage'] = value
        break
      case algoliaParametersFromContentful.NEWEST_ONLY:
        parsedParameters['offerIsNew'] = value
        break
      case algoliaParametersFromContentful.TAGS:
        parsedParameters['tags'] = value
        break
      case algoliaParametersFromContentful.IS_DIGITAL:
        offerTypes['isDigital'] = value
        break
      case algoliaParametersFromContentful.IS_EVENT:
        offerTypes['isEvent'] = value
        break
      case algoliaParametersFromContentful.IS_THING:
        offerTypes['isThing'] = value
        break
    }
  })
  const offerTypesProvided = keys.includes(algoliaParametersFromContentful.IS_DIGITAL) || keys.includes(algoliaParametersFromContentful.IS_EVENT) || keys.includes(algoliaParametersFromContentful.IS_THING)
  if(offerTypesProvided){
    parsedParameters['offerTypes'] = offerTypes
  }
  return parsedParameters
}
