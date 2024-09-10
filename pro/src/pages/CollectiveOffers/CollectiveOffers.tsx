import { useSelector } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import { CollectiveOfferType } from 'apiClient/v1'
import { AppLayout } from 'app/AppLayout'
import {
  GET_COLLECTIVE_OFFERS_BOOKABLE_QUERY_KEY,
  GET_COLLECTIVE_OFFERS_QUERY_KEY,
  GET_OFFERER_QUERY_KEY,
  GET_VENUES_QUERY_KEY,
} from 'config/swrQueryKeys'
import {
  DEFAULT_COLLECTIVE_BOOKABLE_SEARCH_FILTERS,
  DEFAULT_COLLECTIVE_SEARCH_FILTERS,
  DEFAULT_PAGE,
} from 'core/Offers/constants'
import { useQueryCollectiveSearchFilters } from 'core/Offers/hooks/useQuerySearchFilters'
import { CollectiveSearchFiltersParams } from 'core/Offers/types'
import { computeCollectiveOffersUrl } from 'core/Offers/utils/computeCollectiveOffersUrl'
import { hasCollectiveSearchFilters } from 'core/Offers/utils/hasSearchFilters'
import { serializeApiCollectiveFilters } from 'core/Offers/utils/serializer'
import { useActiveFeature } from 'hooks/useActiveFeature'
import { useCurrentUser } from 'hooks/useCurrentUser'
import { useIsNewInterfaceActive } from 'hooks/useIsNewInterfaceActive'
import { formatAndOrderVenues } from 'repository/venuesService'
import { CollectiveOffersScreen } from 'screens/CollectiveOffersScreen/CollectiveOffersScreen'
import { selectCurrentOffererId } from 'store/user/selectors'

export const CollectiveOffers = (): JSX.Element => {
  const isNewOffersAndBookingsActive = useActiveFeature(
    'WIP_ENABLE_NEW_COLLECTIVE_OFFERS_AND_BOOKINGS_STRUCTURE'
  )

  const navigate = useNavigate()
  const { currentUser } = useCurrentUser()
  const isNewInterfaceActive = useIsNewInterfaceActive()
  const selectedOffererId = useSelector(selectCurrentOffererId)

  const defaultCollectiveFilters = isNewOffersAndBookingsActive
    ? DEFAULT_COLLECTIVE_BOOKABLE_SEARCH_FILTERS
    : DEFAULT_COLLECTIVE_SEARCH_FILTERS

  const urlSearchFilters = useQueryCollectiveSearchFilters({
    ...defaultCollectiveFilters,
    offererId: selectedOffererId?.toString() ?? 'all',
  })

  const currentPageNumber = urlSearchFilters.page ?? DEFAULT_PAGE
  const offererId = isNewInterfaceActive
    ? selectedOffererId
    : urlSearchFilters.offererId

  const offererQuery = useSWR(
    [GET_OFFERER_QUERY_KEY, offererId],
    ([, offererIdParam]) =>
      offererId === defaultCollectiveFilters.offererId
        ? null
        : api.getOfferer(Number(offererIdParam)),
    { fallbackData: null }
  )
  const offerer = offererQuery.data

  const { data } = useSWR(
    [GET_VENUES_QUERY_KEY, offerer?.id],
    ([, offererIdParam]) => api.getVenues(null, null, offererIdParam),
    { fallbackData: { venues: [] } }
  )

  const venues = formatAndOrderVenues(data.venues)

  const redirectWithUrlFilters = (filters: CollectiveSearchFiltersParams) => {
    navigate(computeCollectiveOffersUrl(filters, defaultCollectiveFilters), {
      replace: true,
    })
  }

  const isFilterByVenueOrOfferer = hasCollectiveSearchFilters(
    urlSearchFilters,
    defaultCollectiveFilters,
    ['venueId', 'offererId']
  )
  //  Admin users are not allowed to check all offers at once or to use the status filter for performance reasons. Unless there is a venue or offerer filter active.
  const isRestrictedAsAdmin = currentUser.isAdmin && !isFilterByVenueOrOfferer

  const apiFilters: CollectiveSearchFiltersParams = {
    ...defaultCollectiveFilters,
    ...urlSearchFilters,
    ...(isRestrictedAsAdmin ? { status: [] } : {}),
    ...(isNewInterfaceActive
      ? { offererId: selectedOffererId?.toString() ?? 'all' }
      : {}),
  }
  delete apiFilters.page

  const offersQuery = useSWR(
    [
      isNewOffersAndBookingsActive
        ? GET_COLLECTIVE_OFFERS_BOOKABLE_QUERY_KEY
        : GET_COLLECTIVE_OFFERS_QUERY_KEY,
      apiFilters,
    ],
    () => {
      const {
        nameOrIsbn,
        offererId,
        venueId,
        categoryId,
        status,
        creationMode,
        periodBeginningDate,
        periodEndingDate,
        collectiveOfferType,
        format,
      } = serializeApiCollectiveFilters(apiFilters, defaultCollectiveFilters)

      return api.getCollectiveOffers(
        nameOrIsbn,
        offererId,
        status,
        venueId,
        categoryId,
        creationMode,
        periodBeginningDate,
        periodEndingDate,
        isNewOffersAndBookingsActive
          ? CollectiveOfferType.OFFER
          : collectiveOfferType,
        format
      )
    },
    { fallbackData: [] }
  )

  return (
    <AppLayout>
      <CollectiveOffersScreen
        currentPageNumber={currentPageNumber}
        currentUser={currentUser}
        initialSearchFilters={apiFilters}
        isLoading={offersQuery.isLoading}
        offerer={offerer}
        offers={offersQuery.data}
        redirectWithUrlFilters={redirectWithUrlFilters}
        urlSearchFilters={urlSearchFilters}
        venues={venues}
        isRestrictedAsAdmin={isRestrictedAsAdmin}
      />
    </AppLayout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = CollectiveOffers
