import { useMemo } from 'react'
import { useLocation } from 'react-router-dom'

import { Audience } from 'core/shared/types'
import { translateQueryParamsToApiParams } from 'utils/translate'

import { DEFAULT_COLLECTIVE_SEARCH_FILTERS } from '../constants'
import { SearchFiltersParams } from '../types'

export const useCollectiveQuerySearchFilters = () => {
  const { search } = useLocation()

  const urlSearchFilters: SearchFiltersParams = useMemo(() => {
    const urlParams = new URLSearchParams(search)
    const apiParams: Record<string, string | string[]> = {}
    urlParams.forEach((value, key) => {
      if (apiParams[key]) {
        if (!Array.isArray(apiParams[key])) {
          apiParams[key] = [apiParams[key]]
        }
        apiParams[key].push(value)
      } else {
        apiParams[key] = value
      }
    })

    const translatedQuery = translateQueryParamsToApiParams(
      {
        ...apiParams,
      },
      Audience.COLLECTIVE
    )

    const urlFilters = {
      ...DEFAULT_COLLECTIVE_SEARCH_FILTERS,
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
