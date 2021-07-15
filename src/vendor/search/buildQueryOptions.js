import { RESULT_FIELDS } from './constants'
import { buildFacetFilters } from './filters/buildFacetFilters'
import { buildGeolocationFilter } from './filters/buildGeolocationFilter'
import { buildNumericFilters } from './filters/buildNumericFilters'

export const buildQueryOptions = (params, page) => ({
  result_fields: RESULT_FIELDS,
  filters: {
    all: [
      ...buildFacetFilters(params),
      ...buildNumericFilters(params),
      ...buildGeolocationFilter(params),
    ],
  },
  page: {
    // pagination starts at 1 for AppSearch and 0 for Algolia
    // The code is still using Algolia's starting index.
    // TODO(antoinewg). Once the migration is complete, start pagination at 1
    current: typeof page === 'number' ? page + 1 : 1,
    size: params.hitsPerPage || 20,
  },
})
