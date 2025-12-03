import { useNavigate } from 'react-router'
import useSWR from 'swr'

import { api } from '@/apiClient/api'
import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import { GET_COLLECTIVE_OFFERS_BOOKABLE_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import {
  DEFAULT_COLLECTIVE_BOOKABLE_SEARCH_FILTERS,
  DEFAULT_PAGE,
} from '@/commons/core/Offers/constants'
import { useQueryCollectiveSearchFilters } from '@/commons/core/Offers/hooks/useQuerySearchFilters'
import type { CollectiveSearchFiltersParams } from '@/commons/core/Offers/types'
import { computeCollectiveOffersUrl } from '@/commons/core/Offers/utils/computeCollectiveOffersUrl'
import { serializeApiCollectiveFilters } from '@/commons/core/Offers/utils/serializeApiCollectiveFilters'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { ensureCurrentOfferer } from '@/commons/store/offerer/selectors'
import { ensureSelectedVenue } from '@/commons/store/user/selectors'
import { getStoredFilterConfig } from '@/components/OffersTableSearch/utils'

import { CollectiveOffersScreen } from './components/CollectiveOffersScreen/CollectiveOffersScreen'

export const CollectiveOffers = (): JSX.Element => {
  const withSwitchVenueFeature = useActiveFeature('WIP_SWITCH_VENUE')

  const urlSearchFilters = useQueryCollectiveSearchFilters()
  const { storedFilters } = getStoredFilterConfig('collective')
  const finalSearchFilters = {
    ...(storedFilters as Partial<CollectiveSearchFiltersParams>),
    ...urlSearchFilters,
  }

  const navigate = useNavigate()

  const selectedOffererId = useAppSelector(ensureCurrentOfferer).id
  const selectedVenue = useAppSelector(ensureSelectedVenue)

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

  const apiFilters: CollectiveSearchFiltersParams = {
    ...DEFAULT_COLLECTIVE_BOOKABLE_SEARCH_FILTERS,
    ...finalSearchFilters,
    ...{ offererId: selectedOffererId.toString() },
    ...(withSwitchVenueFeature ? { venueId: selectedVenue.id.toString() } : {}),
  }
  delete apiFilters.page

  const offersQuery = useSWR(
    [GET_COLLECTIVE_OFFERS_BOOKABLE_QUERY_KEY, apiFilters],
    () => {
      const params = serializeApiCollectiveFilters(apiFilters)

      return api.getCollectiveOffers(
        params.name,
        params.offererId,
        params.status,
        params.venueId,
        params.periodBeginningDate,
        params.periodEndingDate,
        params.format,
        params.locationType,
        params.offererAddressId
      )
    },
    { fallbackData: [] }
  )

  return (
    <BasicLayout mainHeading={'Offres réservables'}>
      <CollectiveOffersScreen
        currentPageNumber={currentPageNumber}
        initialSearchFilters={apiFilters}
        isLoading={offersQuery.isLoading}
        offererId={selectedOffererId.toString()}
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
