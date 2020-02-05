import algoliasearch from 'algoliasearch'

import {
  WEBAPP_ALGOLIA_APPLICATION_ID,
  WEBAPP_ALGOLIA_INDEX_NAME,
  WEBAPP_ALGOLIA_SEARCH_API_KEY,
} from '../../../../utils/config'

export const fetch = (keywords = '', page = 0, aroundLatLng = '') => {
  if (!keywords) {
    return
  }
  const client = algoliasearch(WEBAPP_ALGOLIA_APPLICATION_ID, WEBAPP_ALGOLIA_SEARCH_API_KEY)
  const index = client.initIndex(WEBAPP_ALGOLIA_INDEX_NAME)

  return index.search({
    aroundLatLng: aroundLatLng,
    aroundRadius: 'all',
    query: keywords,
    page: page,
  })
}
