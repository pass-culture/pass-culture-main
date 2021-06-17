import { stringify } from '../../../../utils/query-string'
import { mapApiToBrowser, translateApiParamsToQueryParams } from '../../../../utils/translate'
import { ALL_STATUS, DEFAULT_CREATION_MODE, DEFAULT_PAGE } from '../Offers/_constants'

export const computeOffersUrl = (offersSearchFilters, offersPageNumber = 1) => {
  const { creationMode, status } = offersSearchFilters
  const searchFiltersParams = { ...offersSearchFilters }

  if (status && status !== ALL_STATUS) {
    searchFiltersParams.status = mapApiToBrowser[status]
  }
  if (creationMode && creationMode !== DEFAULT_CREATION_MODE.id) {
    searchFiltersParams.creationMode = mapApiToBrowser[creationMode]
  }

  if (offersPageNumber !== DEFAULT_PAGE) {
    searchFiltersParams.page = offersPageNumber
  }

  const queryString = stringify(translateApiParamsToQueryParams(searchFiltersParams))

  return queryString ? `/offres?${queryString}` : '/offres'
}
