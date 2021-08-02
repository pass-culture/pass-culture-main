import { buildAlgoliaHit } from './buildAlgoliaHit'
import { buildQueryOptions } from './buildQueryOptions'
import { client } from './client'
import { AppSearchFields, RESULT_FIELDS } from './constants'

// Used for the recommendation module on the homepage
export const fetchHits = async ids => {
  const options = {
    result_fields: RESULT_FIELDS,
    filters: { any: ids.map(id => ({ [AppSearchFields.id]: id })) },
  }

  const response = await client.search('', options)
  return { results: response.results.map(buildAlgoliaHit) }
}

// Used for contentful modules on homepage
export const fetchHomeSearch = async parameters => {
  const options = buildQueryOptions(parameters)

  const response = await client.search('', options)
  const { results, info } = response

  return {
    hits: results.map(buildAlgoliaHit),
    nbHits: info.meta.page.total_results,
  }
}

// Used for the search page
export const fetchSearch = async params => {
  const options = buildQueryOptions(params, params.page)

  const response = await client.search(params.keywords, options)
  const { meta } = response.info

  return {
    hits: response.results.map(buildAlgoliaHit),
    nbHits: meta.page.total_results,
    page: meta.page.current,
    nbPages: meta.page.total_pages,
  }
}
