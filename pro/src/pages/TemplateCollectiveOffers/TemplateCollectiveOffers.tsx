import { useNavigate } from 'react-router'
import useSWR from 'swr'

import { apiNew } from '@/apiClient/api'
import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import {
  DEFAULT_COLLECTIVE_SEARCH_FILTERS,
  DEFAULT_PAGE,
} from '@/commons/core/Offers/constants'
import { useCollectiveOffersSwrKeys } from '@/commons/core/Offers/hooks/useCollectiveOffersSwrKeys'
import { useQueryCollectiveSearchFilters } from '@/commons/core/Offers/hooks/useQuerySearchFilters'
import type { CollectiveSearchFiltersParams } from '@/commons/core/Offers/types'
import { computeCollectiveOffersUrl } from '@/commons/core/Offers/utils/computeCollectiveOffersUrl'
import { serializeApiCollectiveFilters } from '@/commons/core/Offers/utils/serializeApiCollectiveFilters'
import { TemplateCollectiveOffersScreen } from '@/pages/TemplateCollectiveOffers/TemplateCollectiveOffersScreen/TemplateCollectiveOffersScreen'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

export const TemplateCollectiveOffers = () => {
  const urlSearchFilters = useQueryCollectiveSearchFilters()

  const currentPageNumber = urlSearchFilters.page ?? DEFAULT_PAGE
  const navigate = useNavigate()

  const redirectWithUrlFilters = (
    filters: Partial<CollectiveSearchFiltersParams>
  ) => {
    // The offererId and partner venueId come from the Redux store, no need
    // to also reflect them in the URL.
    delete filters.offererId
    delete filters.venueId

    navigate(
      computeCollectiveOffersUrl(
        filters,
        DEFAULT_COLLECTIVE_SEARCH_FILTERS,
        true
      ),
      { replace: true }
    )
  }

  const [queryKey, apiFilters] = useCollectiveOffersSwrKeys({
    isInTemplateOffersPage: true,
  })

  const offersQuery = useSWR(
    [queryKey, apiFilters],
    () => {
      const params = serializeApiCollectiveFilters(apiFilters)
      return apiNew.getCollectiveOfferTemplates({ query: { ...params } })
    },
    { fallbackData: [] }
  )

  return (
    <BasicLayout mainHeading="Offres vitrines">
      {offersQuery.isLoading ? (
        <Spinner />
      ) : (
        <TemplateCollectiveOffersScreen
          currentPageNumber={currentPageNumber}
          initialSearchFilters={apiFilters}
          isLoading={offersQuery.isLoading}
          offers={offersQuery.data ?? []}
          redirectWithUrlFilters={redirectWithUrlFilters}
          urlSearchFilters={urlSearchFilters}
        />
      )}
    </BasicLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = TemplateCollectiveOffers
