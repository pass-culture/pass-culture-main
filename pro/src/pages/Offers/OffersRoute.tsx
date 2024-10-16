import { useSelector } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import { AppLayout } from 'app/AppLayout'
import {
  GET_CATEGORIES_QUERY_KEY,
  GET_OFFERER_ADDRESS_QUERY_KEY,
  GET_OFFERER_QUERY_KEY,
  GET_VENUES_QUERY_KEY,
} from 'commons/config/swrQueryKeys'
import {
  ALL_STATUS,
  DEFAULT_PAGE,
  DEFAULT_SEARCH_FILTERS,
} from 'commons/core/Offers/constants'
import { useQuerySearchFilters } from 'commons/core/Offers/hooks/useQuerySearchFilters'
import { SearchFiltersParams } from 'commons/core/Offers/types'
import { computeIndividualOffersUrl } from 'commons/core/Offers/utils/computeIndividualOffersUrl'
import { hasSearchFilters } from 'commons/core/Offers/utils/hasSearchFilters'
import { serializeApiFilters } from 'commons/core/Offers/utils/serializer'
import { Audience } from 'commons/core/shared/types'
import { useCurrentUser } from 'commons/hooks/useCurrentUser'
import { useIsNewInterfaceActive } from 'commons/hooks/useIsNewInterfaceActive'
import { selectCurrentOffererId } from 'commons/store/user/selectors'
import { sortByLabel } from 'commons/utils/strings'
import { IndividualOffersScreen } from 'pages/Offers/components/IndividualOffersScreen/IndividualOffersScreen'
import {
  formatAndOrderAddresses,
  formatAndOrderVenues,
} from 'repository/venuesService'
import { Spinner } from 'ui-kit/Spinner/Spinner'

export const GET_OFFERS_QUERY_KEY = 'listOffers'

export const OffersRoute = (): JSX.Element => {
  const urlSearchFilters = useQuerySearchFilters()
  const currentPageNumber = urlSearchFilters.page ?? DEFAULT_PAGE
  const navigate = useNavigate()
  const { currentUser } = useCurrentUser()
  const selectedOffererId = useSelector(selectCurrentOffererId)
  const isNewInterfaceActive = useIsNewInterfaceActive()

  const offererQuery = useSWR(
    [
      GET_OFFERER_QUERY_KEY,
      isNewInterfaceActive ? selectedOffererId : urlSearchFilters.offererId,
    ],
    ([, offererIdParam]) =>
      offererIdParam === DEFAULT_SEARCH_FILTERS.offererId
        ? null
        : api.getOfferer(Number(offererIdParam)),
    { fallbackData: null }
  )
  const offerer = offererQuery.data

  const categoriesQuery = useSWR(
    [GET_CATEGORIES_QUERY_KEY],
    () => api.getCategories(),
    { fallbackData: { categories: [], subcategories: [] } }
  )

  const categoriesOptions = sortByLabel(
    categoriesQuery.data.categories
      .filter((category) => category.isSelectable)
      .map((category) => ({
        value: category.id,
        label: category.proLabel,
      }))
  )

  const redirectWithUrlFilters = (
    filters: SearchFiltersParams & { audience?: Audience }
  ) => {
    navigate(computeIndividualOffersUrl(filters), { replace: true })
  }

  const { data } = useSWR(
    [GET_VENUES_QUERY_KEY, offerer?.id],
    ([, offererIdParam]) => api.getVenues(null, null, offererIdParam),
    { fallbackData: { venues: [] } }
  )
  const venues = formatAndOrderVenues(data.venues)

  const offererAddressQuery = useSWR(
    [GET_OFFERER_ADDRESS_QUERY_KEY, offerer?.id],
    ([, offererIdParam]) =>
      offererIdParam ? api.getOffererAddresses(offererIdParam, false) : [],
    { fallbackData: [] }
  )
  const offererAddresses = formatAndOrderAddresses(offererAddressQuery.data)

  const isFilterByVenueOrOfferer = hasSearchFilters(
    urlSearchFilters,
    isNewInterfaceActive ? ['venueId'] : ['venueId', 'offererId']
  )
  //  Admin users are not allowed to check all offers at once or to use the status filter for performance reasons. Unless there is a venue or offerer filter active.
  const isRestrictedAsAdmin = currentUser.isAdmin && !isFilterByVenueOrOfferer

  const apiFilters: SearchFiltersParams = {
    ...DEFAULT_SEARCH_FILTERS,
    ...urlSearchFilters,
    ...(isRestrictedAsAdmin ? { status: ALL_STATUS } : {}),
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

  const offersQuery = useSWR([GET_OFFERS_QUERY_KEY, apiFilters], () => {
    const {
      nameOrIsbn,
      offererId,
      venueId,
      categoryId,
      status,
      creationMode,
      periodBeginningDate,
      periodEndingDate,
      offererAddressId,
      collectiveOfferType,
    } = serializeApiFilters(apiFilters)

    return api.listOffers(
      nameOrIsbn,
      offererId,
      status,
      venueId,
      categoryId,
      creationMode,
      periodBeginningDate,
      periodEndingDate,
      collectiveOfferType,
      offererAddressId
    )
  })

  const offers = offersQuery.data || []

  return (
    <AppLayout>
      {offererQuery.isLoading ? (
        <Spinner />
      ) : (
        <IndividualOffersScreen
          categories={categoriesOptions}
          currentPageNumber={currentPageNumber}
          currentUser={currentUser}
          initialSearchFilters={apiFilters}
          isLoading={offersQuery.isLoading}
          offerer={offerer}
          offers={offers}
          redirectWithUrlFilters={redirectWithUrlFilters}
          urlSearchFilters={urlSearchFilters}
          venues={venues}
          offererAddresses={offererAddresses}
          isRestrictedAsAdmin={isRestrictedAsAdmin}
        />
      )}
    </AppLayout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = OffersRoute
