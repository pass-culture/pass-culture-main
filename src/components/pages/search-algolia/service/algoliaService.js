import algoliasearch from 'algoliasearch'
import { ALGOLIA_APPLICATION_ID, ALGOLIA_INDEX_NAME, ALGOLIA_SEARCH_API_KEY } from '../../../../utils/config'

export const fetch = (keywords = '', page = 0) => {
  if (!keywords) {
    return
  }
  const client = algoliasearch(ALGOLIA_APPLICATION_ID, ALGOLIA_SEARCH_API_KEY)
  const index = client.initIndex(ALGOLIA_INDEX_NAME)

  return index.search({ query: keywords, page: page })
}
