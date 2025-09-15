import { useSelector } from 'react-redux'
import { useNavigate } from 'react-router'
import useSWR from 'swr'

import { api } from '@/apiClient/api'
import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import {
  DEFAULT_COLLECTIVE_TEMPLATE_SEARCH_FILTERS,
  DEFAULT_PAGE,
} from '@/commons/core/Offers/constants'
import { useQueryCollectiveSearchFilters } from '@/commons/core/Offers/hooks/useQuerySearchFilters'
import type { CollectiveSearchFiltersParams } from '@/commons/core/Offers/types'
import { computeCollectiveOffersUrl } from '@/commons/core/Offers/utils/computeCollectiveOffersUrl'
import { getCollectiveOffersSwrKeys } from '@/commons/core/Offers/utils/getCollectiveOffersSwrKeys'
import { serializeApiCollectiveFilters } from '@/commons/core/Offers/utils/serializer'
import { useOfferer } from '@/commons/hooks/swr/useOfferer'
import { selectCurrentOffererId } from '@/commons/store/offerer/selectors'
import { getStoredFilterConfig } from '@/components/OffersTable/OffersTableSearch/utils'
import { TemplateCollectiveOffersScreen } from '@/pages/TemplateCollectiveOffers/TemplateCollectiveOffersScreen/TemplateCollectiveOffersScreen'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

export const TemplateCollectiveOffers = (): JSX.Element => {
  const urlSearchFilters = useQueryCollectiveSearchFilters()
  const { storedFilters } = getStoredFilterConfig('template')
  const finalSearchFilters = {
    ...urlSearchFilters,
    ...(storedFilters as Partial<CollectiveSearchFiltersParams>),
  }
  const offererId = useSelector(selectCurrentOffererId)?.toString()

  const currentPageNumber = finalSearchFilters.page ?? DEFAULT_PAGE
  const navigate = useNavigate()

  const { data: offerer } = useOfferer(
    offererId !== DEFAULT_COLLECTIVE_TEMPLATE_SEARCH_FILTERS.offererId
      ? offererId
      : null,
    true
  )

  const redirectWithUrlFilters = (
    filters: Partial<CollectiveSearchFiltersParams>
  ) => {
    // We dont need to pass the offererId in the URL since
    // its already present in the redux store (useSelector(selectCurrentOffererId))
    delete filters.offererId

    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    navigate(
      computeCollectiveOffersUrl(
        filters,
        DEFAULT_COLLECTIVE_TEMPLATE_SEARCH_FILTERS,
        true
      ),
      { replace: true }
    )
  }

  const collectiveOffersQueryKeys = getCollectiveOffersSwrKeys({
    isNewOffersAndBookingsActive: true,
    isInTemplateOffersPage: true,
    urlSearchFilters: finalSearchFilters,
    selectedOffererId: offererId ?? '',
  })

  const apiFilters: CollectiveSearchFiltersParams = {
    ...DEFAULT_COLLECTIVE_TEMPLATE_SEARCH_FILTERS,
    ...finalSearchFilters,
    ...{ offererId: offererId ?? '' },
  }
  delete apiFilters.page

  const offersQuery = useSWR(
    collectiveOffersQueryKeys,
    () => {
      const params = serializeApiCollectiveFilters(
        apiFilters,
        DEFAULT_COLLECTIVE_TEMPLATE_SEARCH_FILTERS,
        true
      )

      return api.getCollectiveOffers(
        params.nameOrIsbn,
        params.offererId,
        params.status,
        params.venueId,
        params.creationMode,
        params.periodBeginningDate,
        params.periodEndingDate,
        params.collectiveOfferType,
        params.format,
        params.locationType,
        params.offererAddressId
      )
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
          offerer={offerer}
          offers={offersQuery.data}
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
