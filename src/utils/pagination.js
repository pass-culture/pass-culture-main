import invert from 'lodash.invert'
import { getObjectWithMappedKeys } from 'pass-culture-shared'

export const mapWindowToApi = {
  lieu: 'venueId',
  // [`mots-cles`]: 'keywords',
  [`mots-cles`]: 'search',
  structure: 'offererId',
}

export const mapApiToWindow = invert(mapWindowToApi)

export const windowToApiQuery = windowQuery =>
  getObjectWithMappedKeys(windowQuery, mapWindowToApi)
