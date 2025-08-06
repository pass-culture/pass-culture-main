import { useMemo } from 'react'
import { useLocation } from 'react-router'

import { Audience } from '@/commons/core/shared/types'
import { parseUrlParams } from '@/commons/utils/parseUrlParams'
import { translateQueryParamsToApiParams } from '@/commons/utils/translate'

import { CollectiveSearchFiltersParams, SearchFiltersParams } from '../types'

export const useQuerySearchFilters = (): Partial<SearchFiltersParams> => {
  const { search } = useLocation()

  const urlSearchFilters = useMemo(() => {
    const urlParams = new URLSearchParams(search)
    const queryParams = parseUrlParams(urlParams)

    const urlFilters: Partial<SearchFiltersParams> =
      translateQueryParamsToApiParams(
        {
          ...queryParams,
        },
        Audience.INDIVIDUAL
      )

    // Convert page type to number
    urlFilters.page =
      typeof urlFilters.page === 'string'
        ? parseInt(urlFilters.page)
        : urlFilters.page

    return urlFilters
  }, [search])

  return urlSearchFilters
}

export const useQueryCollectiveSearchFilters =
  (): Partial<CollectiveSearchFiltersParams> => {
    const { search } = useLocation()

    const urlParams = new URLSearchParams(search)
    const queryParams = parseUrlParams(urlParams)

    const urlFilters: Partial<CollectiveSearchFiltersParams> =
      translateQueryParamsToApiParams(
        {
          ...queryParams,
        },
        Audience.COLLECTIVE
      )

    // Convert page type to number
    urlFilters.page =
      typeof urlFilters.page === 'string'
        ? parseInt(urlFilters.page)
        : urlFilters.page

    if (urlFilters.status && !Array.isArray(urlFilters.status)) {
      urlFilters.status = [urlFilters.status]
    }

    return urlFilters
  }
