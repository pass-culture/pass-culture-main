import algoliasearch from 'algoliasearch'

import {
  WEBAPP_ALGOLIA_APPLICATION_ID,
  WEBAPP_ALGOLIA_INDEX_NAME,
  WEBAPP_ALGOLIA_SEARCH_API_KEY,
} from '../../utils/config'

const CATEGORY_FACET = `offer.label`
const UNLIMITED_RADIUS = 'all'

export const fetchAlgolia = (keywords = '', page = 0, geolocationCoordinates, categories = []) => {
  const searchParameters = {
    page: page,
    ...buildQueryParameter(keywords),
    ...buildCategoryFilterParameter(categories),
    ...buildGeolocationParameter(geolocationCoordinates),
  }

  const client = algoliasearch(WEBAPP_ALGOLIA_APPLICATION_ID, WEBAPP_ALGOLIA_SEARCH_API_KEY)
  const index = client.initIndex(WEBAPP_ALGOLIA_INDEX_NAME)
  return index.search(searchParameters)
}

const buildQueryParameter = keywords => {
  if (keywords) {
    return { query: keywords }
  }
}

const buildCategoryFilterParameter = categories => {
  if (categories.length > 0) {
    return {
      filters: categories.map(category => `${CATEGORY_FACET}:"${category}"`).join(' OR '),
    }
  }
}

const buildGeolocationParameter = geolocationCoordinates => {
  if (geolocationCoordinates) {
    const { longitude, latitude } = geolocationCoordinates
    if (latitude && longitude) {
      return {
        aroundLatLng: `${latitude}, ${longitude}`,
        aroundRadius: UNLIMITED_RADIUS,
      }
    }
  }
}
