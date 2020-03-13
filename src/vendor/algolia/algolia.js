import algoliasearch from 'algoliasearch'

import {
  WEBAPP_ALGOLIA_APPLICATION_ID,
  WEBAPP_ALGOLIA_INDEX_NAME,
  WEBAPP_ALGOLIA_SEARCH_API_KEY,
} from '../../utils/config'
import { FACETS } from './facets'
import { FILTERS } from './filters'

export const fetchAlgolia = (
  keywords = '',
  page = 0,
  geolocationCoordinates,
  categories = [],
  indexSuffix = ''
) => {
  const searchParameters = {
    page: page,
    ...buildCategoryFilterParameter(categories),
    ...buildGeolocationParameter(geolocationCoordinates),
  }

  const client = algoliasearch(WEBAPP_ALGOLIA_APPLICATION_ID, WEBAPP_ALGOLIA_SEARCH_API_KEY)
  const index = client.initIndex(WEBAPP_ALGOLIA_INDEX_NAME + indexSuffix)

  return index.search(keywords, searchParameters)
}

const buildCategoryFilterParameter = categories => {
  if (categories.length > 0) {
    return {
      filters: categories.map(category => `${FACETS.CATEGORY_FACET}:"${category}"`).join(' OR '),
    }
  }
}

const buildGeolocationParameter = coordinates => {
  if (coordinates) {
    const { longitude, latitude } = coordinates
    if (latitude && longitude) {
      return {
        aroundLatLng: `${latitude}, ${longitude}`,
        aroundRadius: FILTERS.UNLIMITED_RADIUS,
      }
    }
  }
}
