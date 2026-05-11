import { useNavigate } from 'react-router'
import useSWR from 'swr'

import { apiNew } from '@/apiClient/api'
import { MainHeading } from '@/app/App/layouts/components/MainHeading/MainHeading'
import {
  DEFAULT_COLLECTIVE_SEARCH_FILTERS,
  DEFAULT_PAGE,
} from '@/commons/core/Offers/constants'
import { useCollectiveOffersSwrKeys } from '@/commons/core/Offers/hooks/useCollectiveOffersSwrKeys'
import { useQueryCollectiveSearchFilters } from '@/commons/core/Offers/hooks/useQuerySearchFilters'
import type { CollectiveSearchFiltersParams } from '@/commons/core/Offers/types'
import { computeCollectiveOffersUrl } from '@/commons/core/Offers/utils/computeCollectiveOffersUrl'
import { serializeApiCollectiveFilters } from '@/commons/core/Offers/utils/serializeApiCollectiveFilters'

import { CollectiveOffersScreen } from './components/CollectiveOffersScreen/CollectiveOffersScreen'

export const CollectiveOffers = () => {
  const urlSearchFilters = useQueryCollectiveSearchFilters()

  const navigate = useNavigate()

  const [queryKey, apiFilters] = useCollectiveOffersSwrKeys({
    isInTemplateOffersPage: false,
  })

  const currentPageNumber = urlSearchFilters.page ?? DEFAULT_PAGE

  const redirectWithUrlFilters = (
    filters: Partial<CollectiveSearchFiltersParams>
  ) => {
    // The offererId and partner venueId come from the Redux store, no need
    // to also reflect them in the URL.
    delete filters.offererId
    delete filters.venueId

    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    navigate(
      computeCollectiveOffersUrl(filters, DEFAULT_COLLECTIVE_SEARCH_FILTERS),
      {
        replace: true,
      }
    )
  }

  const offersQuery = useSWR(
    [queryKey, apiFilters],
    () => {
      const params = serializeApiCollectiveFilters(apiFilters)

      return apiNew.getCollectiveOffers({ query: { ...params } })
    },
    { fallbackData: [] }
  )

  return (
    <>
      <MainHeading mainHeading="Offres réservables" />

      <CollectiveOffersScreen
        currentPageNumber={currentPageNumber}
        initialSearchFilters={apiFilters}
        isLoading={offersQuery.isLoading}
        offers={offersQuery.data || []}
        redirectWithUrlFilters={redirectWithUrlFilters}
        urlSearchFilters={urlSearchFilters}
      />
    </>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = CollectiveOffers
