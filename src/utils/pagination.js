import invert from 'lodash.invert'
import { getObjectWithMappedKeys } from 'pass-culture-shared'

export const mapWindowToApi = {
  date: 'eventOccurrenceIdOrNew',
  lieu: 'venueId',
  [`mots-cles`]: 'keywords',
  structure: 'offererId',
  stock: 'stockIdOrNew',
}

export const mapApiToWindow = invert(mapWindowToApi)

export const windowToApiQuery = windowQuery => getObjectWithMappedKeys(windowQuery, mapWindowToApi)
