import invert from 'lodash.invert'

import { getObjectWithMappedKeys } from 'pass-culture-shared'

export const mapQueryToApi = {
  lieu: 'venueId',
  [`mots-cles`]: 'keywords',
  structure: 'offererId',
}

export const mapApiToQuery = invert(mapQueryToApi)

export const queryToApiParams = queryParams =>
  getObjectWithMappedKeys(queryParams, mapQueryToApi)
