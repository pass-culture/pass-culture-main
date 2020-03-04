import algoliasearch from 'algoliasearch'

import {
  WEBAPP_ALGOLIA_APPLICATION_ID,
  WEBAPP_ALGOLIA_INDEX_NAME,
  WEBAPP_ALGOLIA_SEARCH_API_KEY,
} from '../../../../utils/config'

export const fetchAlgolia = (keywords = '', page = 0, geolocation, categoriesFilter = []) => {
  if (!keywords) {
    return
  }
  const client = algoliasearch(WEBAPP_ALGOLIA_APPLICATION_ID, WEBAPP_ALGOLIA_SEARCH_API_KEY)
  const index = client.initIndex(WEBAPP_ALGOLIA_INDEX_NAME)
  const searchParameters = {
    query: keywords,
    page: page,
  }

  if (categoriesFilter.length > 0) {
    searchParameters.filters = categoriesFilter
      .map(category => `offer.label:"${category}"`)
      .join(' OR ')
  }

  if (geolocation) {
    const { longitude, latitude } = geolocation
    if (latitude && longitude) {
      searchParameters.aroundLatLng = `${latitude}, ${longitude}`
      searchParameters.aroundRadius = 'all'
    }
  }

  return index.search(searchParameters)
}
