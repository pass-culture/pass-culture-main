import { useMemo } from 'react'
import { useLocation } from 'react-router-dom'

import { DEFAULT_PAGE, DEFAULT_SEARCH_FILTERS } from 'core/Offers/constants'
import { parse } from 'utils/query-string'
import { translateQueryParamsToApiParams } from 'utils/translate'

import { Audience } from '../../shared/types'
import { SearchFiltersParams } from '../types'

interface UrlSearchFilters {
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

export const useQuerySearchFilters = (): [
  SearchFiltersParams,
  number,
  Audience,
] => {
  const { search } = useLocation()

  const queryParams: UrlSearchFilters = useMemo(() => parse(search), [search])

  const urlPageNumber: number = useMemo(() => {
    return Number(queryParams.page) || DEFAULT_PAGE
  }, [queryParams])

  const urlOfferType: Audience = useMemo(() => {
    if (isAudienceIndividualOrCollective(queryParams.audience)) {
      return queryParams.audience
    }
    return Audience.INDIVIDUAL
  }, [queryParams])

  const urlSearchFilters: SearchFiltersParams = useMemo(() => {
    const queryParams = parse(search)
    const translatedQuery = translateQueryParamsToApiParams({
      ...queryParams,
    })

    const urlFilters = {
      ...DEFAULT_SEARCH_FILTERS,
      ...translatedQuery,
    }

    return urlFilters
  }, [search])

  return [urlSearchFilters, urlPageNumber, urlOfferType]
}
