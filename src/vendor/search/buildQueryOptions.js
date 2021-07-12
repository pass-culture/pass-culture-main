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
    current: page || 1,
    size: params.hitsPerPage || 20,
  },
})
