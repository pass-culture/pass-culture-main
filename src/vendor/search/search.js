import { buildAlgoliaHit } from './buildAlgoliaHit'
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
