import { buildAlgoliaHit } from './buildAlgoliaHit'
import { buildQueryOptions } from './buildQueryOptions'
import { client } from './client'
import { AppSearchFields, RESULT_FIELDS } from './constants'

// Used for the recommendation module on the homepage
export const fetchHits = ids => {
  const options = {
    result_fields: RESULT_FIELDS,
    filters: { any: ids.map(id => ({ [AppSearchFields.id]: id })) },
  }

  return client.search('', options).then(response => ({
    results: response.results.map(buildAlgoliaHit),
  }))
}

// Used for contentful modules on homepage
export const fetchHomeSearch = parameters => {
  const options = buildQueryOptions(parameters)

  return client.search('', options).then(({ results, info }) => ({
    hits: results.map(buildAlgoliaHit),
    nbHits: info.meta.page.total_results,
  }))
}
