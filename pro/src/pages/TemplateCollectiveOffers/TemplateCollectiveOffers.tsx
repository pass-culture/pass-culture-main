import { useSelector } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import { CollectiveOfferType } from 'apiClient/v1'
import { AppLayout } from 'app/AppLayout'
import {
  GET_OFFERER_QUERY_KEY,
  GET_COLLECTIVE_OFFERS_TEMPLATE_QUERY_KEY,
  GET_VENUES_QUERY_KEY,
} from 'config/swrQueryKeys'
import {
  DEFAULT_COLLECTIVE_TEMPLATE_SEARCH_FILTERS,
  DEFAULT_PAGE,
} from 'core/Offers/constants'
import { useQueryCollectiveSearchFilters } from 'core/Offers/hooks/useQuerySearchFilters'
import { CollectiveSearchFiltersParams } from 'core/Offers/types'
import { computeCollectiveOffersUrl } from 'core/Offers/utils/computeCollectiveOffersUrl'
import { hasCollectiveSearchFilters } from 'core/Offers/utils/hasSearchFilters'
import { serializeApiCollectiveFilters } from 'core/Offers/utils/serializer'
import { useCurrentUser } from 'hooks/useCurrentUser'
import { useIsNewInterfaceActive } from 'hooks/useIsNewInterfaceActive'
import { formatAndOrderVenues } from 'repository/venuesService'
import { TemplateCollectiveOffersScreen } from 'screens/TemplateCollectiveOffersScreen/TemplateCollectiveOffersScreen'
import { selectCurrentOffererId } from 'store/user/selectors'
import { Spinner } from 'ui-kit/Spinner/Spinner'

export const TemplateCollectiveOffers = (): JSX.Element => {
  const selectedOffererId = useSelector(selectCurrentOffererId)

  const urlSearchFilters = useQueryCollectiveSearchFilters({
    ...DEFAULT_COLLECTIVE_TEMPLATE_SEARCH_FILTERS,
    offererId: selectedOffererId?.toString() ?? 'all',
  })

  const currentPageNumber = urlSearchFilters.page ?? DEFAULT_PAGE
  const navigate = useNavigate()
  const { currentUser } = useCurrentUser()
  const isNewInterfaceActive = useIsNewInterfaceActive()
  const offererId = isNewInterfaceActive
    ? selectedOffererId
    : urlSearchFilters.offererId

  const offererQuery = useSWR(
    [GET_OFFERER_QUERY_KEY, offererId],
    ([, offererIdParam]) =>
      offererId === DEFAULT_COLLECTIVE_TEMPLATE_SEARCH_FILTERS.offererId
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
    navigate(
      computeCollectiveOffersUrl(
        filters,
        DEFAULT_COLLECTIVE_TEMPLATE_SEARCH_FILTERS,
        true
      ),
      { replace: true }
    )
  }

  const isFilterByVenueOrOfferer = hasCollectiveSearchFilters(
    urlSearchFilters,
    DEFAULT_COLLECTIVE_TEMPLATE_SEARCH_FILTERS,
    ['venueId', 'offererId']
  )
  //  Admin users are not allowed to check all offers at once or to use the status filter for performance reasons. Unless there is a venue or offerer filter active.
  const isRestrictedAsAdmin = currentUser.isAdmin && !isFilterByVenueOrOfferer

  const apiFilters: CollectiveSearchFiltersParams = {
    ...DEFAULT_COLLECTIVE_TEMPLATE_SEARCH_FILTERS,
    ...urlSearchFilters,
    ...(isRestrictedAsAdmin ? { status: [] } : {}),
    ...(isNewInterfaceActive
      ? { offererId: selectedOffererId?.toString() ?? '' }
      : {}),
  }
  delete apiFilters.page

  const offersQuery = useSWR(
    [GET_COLLECTIVE_OFFERS_TEMPLATE_QUERY_KEY, apiFilters],
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
        format,
      } = serializeApiCollectiveFilters(
        apiFilters,
        DEFAULT_COLLECTIVE_TEMPLATE_SEARCH_FILTERS
      )

      return api.getCollectiveOffers(
        nameOrIsbn,
        offererId,
        status,
        venueId,
        categoryId,
        creationMode,
        periodBeginningDate,
        periodEndingDate,
        CollectiveOfferType.TEMPLATE,
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
        <TemplateCollectiveOffersScreen
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
export const Component = TemplateCollectiveOffers
