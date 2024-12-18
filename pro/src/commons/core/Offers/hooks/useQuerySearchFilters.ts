import { useMemo } from 'react'
import { useLocation } from 'react-router';

import {
  DEFAULT_COLLECTIVE_SEARCH_FILTERS,
  DEFAULT_SEARCH_FILTERS,
} from 'commons/core/Offers/constants'
import { Audience } from 'commons/core/shared/types'
import { parseUrlParams } from 'commons/utils/parseUrlParams'
import { translateQueryParamsToApiParams } from 'commons/utils/translate'

import { CollectiveSearchFiltersParams, SearchFiltersParams } from '../types'

export const useQuerySearchFilters = (): SearchFiltersParams => {
  const { search } = useLocation()

  const urlSearchFilters: SearchFiltersParams = useMemo(() => {
    const urlParams = new URLSearchParams(search)
    const queryParams = parseUrlParams(urlParams)

    const translatedQuery = translateQueryParamsToApiParams(
      {
        ...queryParams,
      },
      Audience.INDIVIDUAL
    )

    const urlFilters = {
      ...DEFAULT_SEARCH_FILTERS,
      ...translatedQuery,
    }

    // Convert page type to number
    urlFilters.page =
      typeof urlFilters.page === 'string'
        ? parseInt(urlFilters.page)
        : urlFilters.page

    return urlFilters
  }, [search])

  return urlSearchFilters
}

export const useQueryCollectiveSearchFilters = (
  defaultCollectiveSearchFilters: CollectiveSearchFiltersParams = DEFAULT_COLLECTIVE_SEARCH_FILTERS
): CollectiveSearchFiltersParams => {
  const { search } = useLocation()

  const urlParams = new URLSearchParams(search)
  const queryParams = parseUrlParams(urlParams)

  const translatedQuery = translateQueryParamsToApiParams(
    {
      ...queryParams,
    },
    Audience.COLLECTIVE
  )

  const urlFilters = {
    ...defaultCollectiveSearchFilters,
    ...translatedQuery,
  }

  // Convert page type to number
  urlFilters.page =
    typeof urlFilters.page === 'string'
      ? parseInt(urlFilters.page)
      : urlFilters.page

  return urlFilters
}
