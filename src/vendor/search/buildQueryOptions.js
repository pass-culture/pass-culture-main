import { RESULT_FIELDS } from './constants'
import { buildFacetFilters } from './filters/buildFacetFilters'
import { buildNumericFilters } from './filters/buildNumericFilters'

export const buildQueryOptions = params => ({
  result_fields: RESULT_FIELDS,
  filters: {
    all: [...buildFacetFilters(params), ...buildNumericFilters(params)],
  },
  page: {
    current: 1,
    size: params.hitsPerPage || 20,
  },
})
