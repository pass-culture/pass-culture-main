import { AppSearchFields, RESULT_FIELDS } from './constants'
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
  group: {
    // This ensures that only one offer of each group is retrieved.
    // Ex: when we look for a book, we only show one per isbn (one per visa for the movies).
    // See https://www.elastic.co/fr/blog/advanced-search-queries-in-elastic-app-search
    field: AppSearchFields.group,
  },
  page: {
    // pagination starts at 1 for AppSearch and 0 for Algolia
    // The code is still using Algolia's starting index.
    // TODO(antoinewg). Once the migration is complete, start pagination at 1
    current: typeof page === 'number' ? page + 1 : 1,
    size: params.hitsPerPage || 20,
  },
})
