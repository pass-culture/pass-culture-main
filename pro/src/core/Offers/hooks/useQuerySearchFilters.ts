import { useMemo } from 'react'
import { useLocation } from 'react-router-dom'

import { DEFAULT_PAGE, DEFAULT_SEARCH_FILTERS } from 'core/Offers/constants'
import { parse } from 'utils/query-string'
import {
  mapBrowserToApi,
  translateQueryParamsToApiParams,
} from 'utils/translate'

import { Audience } from '../../shared/types'
import { TSearchFilters } from '../types'

interface IUrlSearchFilters {
  nameOrIsbn?: string
  offererId?: string
  venueId?: string
  categoryId?: string
  statut?: string
  creation?: string
  periodBeginningDate?: string
  periodEndingDate?: string
  audience?: string
  page?: string
}

const isAudienceIndividualOrCollective = (
  audience?: string
): audience is Audience =>
  audience === Audience.INDIVIDUAL || audience === Audience.COLLECTIVE

const useQuerySearchFilters = (): [TSearchFilters, number, Audience] => {
  const { search } = useLocation()

  const queryParams: IUrlSearchFilters = useMemo(() => parse(search), [search])

  const urlPageNumber: number = useMemo(() => {
    return Number(queryParams.page) || DEFAULT_PAGE
  }, [queryParams])

  const urlOfferType: Audience = useMemo(() => {
    if (isAudienceIndividualOrCollective(queryParams.audience)) {
      return queryParams.audience
    }
    return Audience.INDIVIDUAL
  }, [queryParams])

  const urlSearchFilters: TSearchFilters = useMemo(() => {
    const translatedFilters: Record<string, string> = {}

    const fieldsWithTranslatedValues = ['statut', 'creation'] as const
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
  }, [queryParams])

  return [urlSearchFilters, urlPageNumber, urlOfferType]
}

export default useQuerySearchFilters
