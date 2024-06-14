import { useNavigate } from 'react-router-dom'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import { CollectiveOfferDisplayedStatus } from 'apiClient/v1'
import { AppLayout } from 'app/AppLayout'
import {
  GET_COLLECTIVE_OFFERS_QUERY_KEY,
  GET_OFFERER_QUERY_KEY,
  GET_VENUES_QUERY_KEY,
} from 'config/swrQueryKeys'
import {
  ALL_STATUS,
  DEFAULT_PAGE,
  DEFAULT_SEARCH_FILTERS,
} from 'core/Offers/constants'
import { useQuerySearchFilters } from 'core/Offers/hooks/useQuerySearchFilters'
import { SearchFiltersParams } from 'core/Offers/types'
import { computeCollectiveOffersUrl } from 'core/Offers/utils/computeOffersUrl'
import { hasSearchFilters } from 'core/Offers/utils/hasSearchFilters'
import { serializeApiFilters } from 'core/Offers/utils/serializer'
import { Audience } from 'core/shared/types'
import { useCurrentUser } from 'hooks/useCurrentUser'
import { formatAndOrderVenues } from 'repository/venuesService'
import { Offers } from 'screens/Offers/Offers'
import { Spinner } from 'ui-kit/Spinner/Spinner'

export const CollectiveOffers = (): JSX.Element => {
  const urlSearchFilters = useQuerySearchFilters()
  const currentPageNumber = urlSearchFilters.page ?? DEFAULT_PAGE
  const navigate = useNavigate()
  const { currentUser } = useCurrentUser()

  const offererQuery = useSWR(
    [GET_OFFERER_QUERY_KEY, urlSearchFilters.offererId],
    ([, offererIdParam]) =>
      urlSearchFilters.offererId === DEFAULT_SEARCH_FILTERS.offererId
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
    navigate(computeCollectiveOffersUrl(filters))
  }

  const isFilterByVenueOrOfferer = hasSearchFilters(urlSearchFilters, [
    'venueId',
    'offererId',
  ])
  //  Admin users are not allowed to check all offers at once or to use the status filter for performance reasons. Unless there is a venue or offerer filter active.
  const isRestrictedAsAdmin = currentUser.isAdmin && !isFilterByVenueOrOfferer

  const apiFilters: SearchFiltersParams = {
    ...DEFAULT_SEARCH_FILTERS,
    ...urlSearchFilters,
    ...(isRestrictedAsAdmin ? { status: ALL_STATUS } : {}),
  }
  delete apiFilters.page

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
        status as CollectiveOfferDisplayedStatus,
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
          offers={offersQuery.data}
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
