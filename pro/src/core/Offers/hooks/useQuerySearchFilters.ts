import { useMemo } from 'react'
import { useLocation } from 'react-router-dom'

import {
  DEFAULT_COLLECTIVE_SEARCH_FILTERS,
  DEFAULT_SEARCH_FILTERS,
} from 'core/Offers/constants'
import { Audience } from 'core/shared/types'
import { translateQueryParamsToApiParams } from 'utils/translate'

import { SearchFiltersParams } from '../types'

export const useQuerySearchFilters = (
  audience: Audience
): SearchFiltersParams => {
  const { search } = useLocation()

  const urlSearchFilters: SearchFiltersParams = useMemo(() => {
    const urlParams = new URLSearchParams(search)
    const queryParams: Record<string, string | string[]> = {}
    urlParams.forEach((value, key) => {
      if (queryParams[key]) {
        if (!Array.isArray(queryParams[key])) {
          queryParams[key] = [queryParams[key]]
        }
        queryParams[key].push(value)
      } else {
        queryParams[key] = value
      }
    })

    const translatedQuery = translateQueryParamsToApiParams(
      {
        ...queryParams,
      },
      audience
    )

    const urlFilters = {
      ...(audience === Audience.INDIVIDUAL
        ? DEFAULT_SEARCH_FILTERS
        : DEFAULT_COLLECTIVE_SEARCH_FILTERS),
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
