import { getObjectWithMappedKeys } from 'pass-culture-shared'

export const mapQueryToApi = {
  lieu: 'venueId',
  structure: 'offererId',
}

export const queryToApiParams = queryParams =>
  getObjectWithMappedKeys(queryParams, mapQueryToApi)
