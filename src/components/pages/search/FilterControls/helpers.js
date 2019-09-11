import { getFirstChangingKey } from '../helpers'

export const INFINITE_DISTANCE = 20000

export const distanceOptions = [
  {
    label: 'Toutes distances',
    value: INFINITE_DISTANCE,
  },
  {
    label: "Moins d'1 km",
    value: 1,
  },
  {
    label: 'Moins de 10 km',
    value: 10,
  },
  {
    label: 'Moins de 50 km',
    value: 50,
  },
]

export const getCanFilter = (filterParams, queryParams) => {
  const firstChangingKey = getFirstChangingKey(queryParams, filterParams)

  const filterHasChanged = typeof firstChangingKey !== 'undefined'
  if (!filterHasChanged) {
    return false
  }

  if (queryParams['mots-cles']) {
    return true
  }

  /*
  const filterParamsAreEmpty = getVisibleParamsAreEmpty(filterParams)
  if (filterParamsAreEmpty) {
    return false
  }
  */

  return true
}
