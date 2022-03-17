import { useMemo } from 'react'
import { useLocation } from 'react-router-dom'

import { DEFAULT_PAGE, DEFAULT_SEARCH_FILTERS } from 'core/Offers/constants'
import { parse } from 'utils/query-string'
import {
  mapBrowserToApi,
  translateQueryParamsToApiParams,
} from 'utils/translate'

interface IUrlSearchFilters {
  nameOrIsbn: string
  offererId: string
  venueId: string
  categoryId: string
  status: string
  creationMode: string
  periodBeginningDate: string
  periodEndingDate: string
}

const useQuerySearchFilters = (): [IUrlSearchFilters, number] => {
  const { search } = useLocation()

  const urlPageNumber: number = useMemo(() => {
    const queryParams = parse(search)
    return Number(queryParams['page']) || DEFAULT_PAGE
  }, [search])

  const urlSearchFilters: IUrlSearchFilters = useMemo(() => {
    const queryParams = parse(search)

    const translatedFilters: Record<string, string> = {}

    const fieldsWithTranslatedValues = ['statut', 'creation']
    fieldsWithTranslatedValues.forEach(field => {
      if (queryParams[field]) {
        type mapBrowserToApiKey = keyof typeof mapBrowserToApi
        const queryParamsKey: mapBrowserToApiKey = queryParams[
          field
        ] as mapBrowserToApiKey
        const translatedValue = mapBrowserToApi[queryParamsKey]
        translatedFilters[field] = translatedValue
      }
    })
    const translatedQuery = translateQueryParamsToApiParams({
      ...queryParams,
      ...translatedFilters,
    })

    const urlFilters = {
      ...DEFAULT_SEARCH_FILTERS,
      ...translatedQuery,
    }
    return urlFilters
  }, [search])

  return [urlSearchFilters, urlPageNumber]
}

export default useQuerySearchFilters
