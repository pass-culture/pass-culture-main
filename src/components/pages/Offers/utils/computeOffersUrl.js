import { stringify } from '../../../../utils/query-string'
import { mapApiToBrowser, translateApiParamsToQueryParams } from '../../../../utils/translate'
import { ALL_STATUS, DEFAULT_CREATION_MODE } from '../Offers/_constants'

export const computeOffersUrl = offersSearchFilters => {
  const { creationMode, status } = offersSearchFilters
  const searchFiltersParams = { ...offersSearchFilters }

  if (status && status !== ALL_STATUS) {
    searchFiltersParams.status = mapApiToBrowser[status]
  }
  if (creationMode && creationMode !== DEFAULT_CREATION_MODE.id) {
    searchFiltersParams.creationMode = mapApiToBrowser[creationMode]
  }

  const queryString = stringify(translateApiParamsToQueryParams(searchFiltersParams))

  return queryString ? `/offres?${queryString}` : '/offres'
}
