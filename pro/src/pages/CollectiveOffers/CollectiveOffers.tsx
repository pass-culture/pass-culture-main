import { useSelector } from 'react-redux'
import { useNavigate } from 'react-router'
import useSWR from 'swr'

import { api } from '@/apiClient/api'
import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import {
  DEFAULT_COLLECTIVE_BOOKABLE_SEARCH_FILTERS,
  DEFAULT_PAGE,
} from '@/commons/core/Offers/constants'
import { useQueryCollectiveSearchFilters } from '@/commons/core/Offers/hooks/useQuerySearchFilters'
import type { CollectiveSearchFiltersParams } from '@/commons/core/Offers/types'
import { computeCollectiveOffersUrl } from '@/commons/core/Offers/utils/computeCollectiveOffersUrl'
import { getCollectiveOffersSwrKeys } from '@/commons/core/Offers/utils/getCollectiveOffersSwrKeys'
import { serializeApiCollectiveFilters } from '@/commons/core/Offers/utils/serializer'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { selectCurrentOfferer } from '@/commons/store/offerer/selectors'
import { getStoredFilterConfig } from '@/components/OffersTable/OffersTableSearch/utils'

import { CollectiveOffersScreen } from './components/CollectiveOffersScreen/CollectiveOffersScreen'

export const CollectiveOffers = (): JSX.Element => {
  const urlSearchFilters = useQueryCollectiveSearchFilters()
  const { storedFilters } = getStoredFilterConfig('collective')
  const finalSearchFilters = {
    ...(storedFilters as Partial<CollectiveSearchFiltersParams>),
    ...urlSearchFilters,
  }

  const isNewOffersAndBookingsActive = useActiveFeature(
    'WIP_ENABLE_NEW_COLLECTIVE_OFFERS_AND_BOOKINGS_STRUCTURE'
  )

  const navigate = useNavigate()
  const offerer = useSelector(selectCurrentOfferer)

  const currentPageNumber = finalSearchFilters.page ?? DEFAULT_PAGE

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
        DEFAULT_COLLECTIVE_BOOKABLE_SEARCH_FILTERS
      ),
      {
        replace: true,
      }
    )
  }

  const collectiveOffersQueryKeys = getCollectiveOffersSwrKeys({
    isInTemplateOffersPage: false,
    urlSearchFilters: finalSearchFilters,
    selectedOffererId: offerer?.id.toString() ?? '',
  })

  const apiFilters: CollectiveSearchFiltersParams = {
    ...DEFAULT_COLLECTIVE_BOOKABLE_SEARCH_FILTERS,
    ...finalSearchFilters,
    ...{ offererId: offerer?.id?.toString() ?? 'all' },
  }
  delete apiFilters.page

  const offersQuery = useSWR(
    collectiveOffersQueryKeys,
    () => {
      const params = serializeApiCollectiveFilters(
        apiFilters,
        DEFAULT_COLLECTIVE_BOOKABLE_SEARCH_FILTERS,
        isNewOffersAndBookingsActive
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
    <BasicLayout
      mainHeading={
        isNewOffersAndBookingsActive
          ? 'Offres réservables'
          : 'Offres collectives'
      }
    >
      <CollectiveOffersScreen
        currentPageNumber={currentPageNumber}
        initialSearchFilters={apiFilters}
        isLoading={offersQuery.isLoading}
        offerer={offerer}
        offers={offersQuery.data}
        redirectWithUrlFilters={redirectWithUrlFilters}
        urlSearchFilters={urlSearchFilters}
      />
    </BasicLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = CollectiveOffers
