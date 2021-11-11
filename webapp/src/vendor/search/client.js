// disable-next-line import/no-unresolved
import * as ElasticAppSearch from '@elastic/app-search-javascript'

import { APP_SEARCH_KEY, APP_SEARCH_ENDPOINT } from '../../utils/config'

const OFFERS_ENGINE_NAME = 'offers-meta'

export const client = ElasticAppSearch.createClient({
  searchKey: APP_SEARCH_KEY,
  endpointBase: APP_SEARCH_ENDPOINT,
  engineName: OFFERS_ENGINE_NAME,
})
