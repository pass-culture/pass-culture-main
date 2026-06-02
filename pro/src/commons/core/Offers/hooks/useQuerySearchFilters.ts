import { useMemo } from 'react'
import { useLocation } from 'react-router'

import type { ListOffersQueryModel } from '@/apiClient/v1/new'
import { Audience } from '@/commons/core/shared/types'
import { parseUrlParams } from '@/commons/utils/parseUrlParams'
import { translateQueryParamsToApiParams } from '@/commons/utils/translate'
import type { IndividualOffersFilters } from '@/pages/IndividualOffers/common/types'

import type { CollectiveSearchFiltersParams } from '../types'

const NUMERIC_INDIVIDUAL_FIELDS = [
  'venueId',
  'offererAddressId',
] as const satisfies ReadonlyArray<keyof ListOffersQueryModel>

const parseNumericField = (value: unknown): number | undefined => {
  if (typeof value === 'number') {
    return value
  }
  if (typeof value === 'string' && value.trim() !== '') {
    const parsed = Number(value)
    return Number.isNaN(parsed) ? undefined : parsed
  }
  return undefined
}

export const useQuerySearchFilters = (): Partial<IndividualOffersFilters> => {
  const { search } = useLocation()

  return useMemo(() => {
    const urlParams = new URLSearchParams(search)
    const queryParams = parseUrlParams(urlParams)

    const translated = translateQueryParamsToApiParams(
      { ...queryParams },
      Audience.INDIVIDUAL
    ) as Record<string, unknown>

    const result: Partial<IndividualOffersFilters> = {
      ...(translated as Partial<IndividualOffersFilters>),
    }

    for (const field of NUMERIC_INDIVIDUAL_FIELDS) {
      result[field] = parseNumericField(translated[field])
    }

    if (typeof translated.page === 'string') {
      result.page = Number.parseInt(translated.page, 10)
    } else if (typeof translated.page === 'number') {
      result.page = translated.page
    }

    return result
  }, [search])
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
        ? Number.parseInt(urlFilters.page, 10)
        : urlFilters.page

    if (urlFilters.status && !Array.isArray(urlFilters.status)) {
      urlFilters.status = [urlFilters.status]
    }

    return urlFilters
  }
