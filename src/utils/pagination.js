import invert from 'lodash.invert'
import { getObjectWithMappedKeys } from 'pass-culture-shared'

export const mapWindowToApi = {
  jours: 'days',
  [`mots-cles`]: 'keywords',
}

export const mapApiToWindow = invert(mapWindowToApi)

export const windowToApiQuery = windowQuery =>
  getObjectWithMappedKeys(windowQuery, mapWindowToApi)
