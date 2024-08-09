import { useSelector } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import {
  CollectiveOfferDisplayedStatus,
  CollectiveOfferStatus,
} from 'apiClient/v1'
import { AppLayout } from 'app/AppLayout'
import {
  GET_COLLECTIVE_OFFERS_QUERY_KEY,
  GET_OFFERER_QUERY_KEY,
  GET_VENUES_QUERY_KEY,
} from 'config/swrQueryKeys'
import {
  DEFAULT_COLLECTIVE_SEARCH_FILTERS,
  DEFAULT_PAGE,
} from 'core/Offers/constants'
import { useQuerySearchFilters } from 'core/Offers/hooks/useQuerySearchFilters'
import { SearchFiltersParams } from 'core/Offers/types'
import { computeCollectiveOffersUrl } from 'core/Offers/utils/computeOffersUrl'
import { hasSearchFilters } from 'core/Offers/utils/hasSearchFilters'
import { serializeApiFilters } from 'core/Offers/utils/serializer'
import { Audience } from 'core/shared/types'
import { useActiveFeature } from 'hooks/useActiveFeature'
import { useCurrentUser } from 'hooks/useCurrentUser'
import { useIsNewInterfaceActive } from 'hooks/useIsNewInterfaceActive'
import { formatAndOrderVenues } from 'repository/venuesService'
import { Offers } from 'screens/Offers/Offers'
import { selectCurrentOffererId } from 'store/user/selectors'
import { Spinner } from 'ui-kit/Spinner/Spinner'

export const CollectiveOffers = (): JSX.Element => {
  const urlSearchFilters = useQuerySearchFilters(Audience.COLLECTIVE)
  const currentPageNumber = urlSearchFilters.page ?? DEFAULT_PAGE
  const navigate = useNavigate()
  const { currentUser } = useCurrentUser()
  const isNewInterfaceActive = useIsNewInterfaceActive()
  const selectedOffererId = useSelector(selectCurrentOffererId)
  const offererId = isNewInterfaceActive
    ? selectedOffererId
    : urlSearchFilters.offererId

  const isDraftCollectiveOffersEnabled = useActiveFeature(
    'WIP_ENABLE_COLLECTIVE_DRAFT_OFFERS'
  )

  const offererQuery = useSWR(
    [GET_OFFERER_QUERY_KEY, offererId],
    ([, offererIdParam]) =>
      offererId === DEFAULT_COLLECTIVE_SEARCH_FILTERS.offererId
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

  const redirectWithUrlFilters = (
    filters: SearchFiltersParams & { audience?: Audience }
  ) => {
    navigate(computeCollectiveOffersUrl(filters), { replace: true })
  }

  const isFilterByVenueOrOfferer = hasSearchFilters(urlSearchFilters, [
    'venueId',
    'offererId',
  ])
  //  Admin users are not allowed to check all offers at once or to use the status filter for performance reasons. Unless there is a venue or offerer filter active.
  const isRestrictedAsAdmin = currentUser.isAdmin && !isFilterByVenueOrOfferer

  const apiFilters: SearchFiltersParams = {
    ...DEFAULT_COLLECTIVE_SEARCH_FILTERS,
    ...urlSearchFilters,
    ...(isRestrictedAsAdmin ? { status: [] } : {}),
    ...(isNewInterfaceActive
      ? { offererId: selectedOffererId?.toString() ?? '' }
      : {}),
  }
  delete apiFilters.page

  if (
    isNewInterfaceActive &&
    selectedOffererId &&
    selectedOffererId.toString() !== urlSearchFilters.offererId
  ) {
    setTimeout(() => {
      redirectWithUrlFilters(apiFilters)
    })
  }

  const offersQuery = useSWR(
    [GET_COLLECTIVE_OFFERS_QUERY_KEY, apiFilters],
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
      } = serializeApiFilters(apiFilters)

      return api.getCollectiveOffers(
        nameOrIsbn,
        offererId,
        status as CollectiveOfferDisplayedStatus[],
        venueId,
        categoryId,
        creationMode,
        periodBeginningDate,
        periodEndingDate,
        collectiveOfferType,
        format
      )
    },
    { fallbackData: [] }
  )

  const displayedOffers = isDraftCollectiveOffersEnabled
    ? offersQuery.data
    : offersQuery.data.filter(
        (offer) => offer.status !== CollectiveOfferStatus.DRAFT
      )

  return (
    <AppLayout>
      {offersQuery.isLoading ? (
        <Spinner />
      ) : (
        <Offers
          audience={Audience.COLLECTIVE}
          currentPageNumber={currentPageNumber}
          currentUser={currentUser}
          initialSearchFilters={apiFilters}
          isLoading={offersQuery.isLoading}
          offerer={offerer}
          collectiveOffers={displayedOffers}
          redirectWithUrlFilters={redirectWithUrlFilters}
          urlSearchFilters={urlSearchFilters}
          venues={venues}
          isRestrictedAsAdmin={isRestrictedAsAdmin}
        />
      )}
    </AppLayout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = CollectiveOffers
