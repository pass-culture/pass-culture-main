import { useSelector } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import { CollectiveOfferType } from 'apiClient/v1'
import { Layout } from 'app/App/layout/Layout'
import {
  GET_OFFERER_QUERY_KEY,
  GET_VENUES_QUERY_KEY,
} from 'commons/config/swrQueryKeys'
import {
  DEFAULT_COLLECTIVE_TEMPLATE_SEARCH_FILTERS,
  DEFAULT_PAGE,
} from 'commons/core/Offers/constants'
import { useQueryCollectiveSearchFilters } from 'commons/core/Offers/hooks/useQuerySearchFilters'
import { CollectiveSearchFiltersParams } from 'commons/core/Offers/types'
import { computeCollectiveOffersUrl } from 'commons/core/Offers/utils/computeCollectiveOffersUrl'
import { getCollectiveOffersSwrKeys } from 'commons/core/Offers/utils/getCollectiveOffersSwrKeys'
import { hasCollectiveSearchFilters } from 'commons/core/Offers/utils/hasSearchFilters'
import { serializeApiCollectiveFilters } from 'commons/core/Offers/utils/serializer'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { useCurrentUser } from 'commons/hooks/useCurrentUser'
import { selectCurrentOffererId } from 'commons/store/offerer/selectors'
import { getStoredFilterConfig } from 'components/OffersTable/OffersTableSearch/utils'
import { TemplateCollectiveOffersScreen } from 'pages/TemplateCollectiveOffers/TemplateCollectiveOffersScreen/TemplateCollectiveOffersScreen'
import { formatAndOrderVenues } from 'repository/venuesService'
import { Spinner } from 'ui-kit/Spinner/Spinner'

export const TemplateCollectiveOffers = (): JSX.Element => {
  const isToggleAndMemorizeFiltersEnabled = useActiveFeature('WIP_COLLAPSED_MEMORIZED_FILTERS')
  const urlSearchFilters = useQueryCollectiveSearchFilters()
  const { storedFilters } = getStoredFilterConfig('template')
  const finalSearchFilters = {
    ...urlSearchFilters,
    ...isToggleAndMemorizeFiltersEnabled ? (storedFilters as Partial<CollectiveSearchFiltersParams>) : {}
  }
  const offererId = useSelector(selectCurrentOffererId)?.toString()

  const currentPageNumber = finalSearchFilters.page ?? DEFAULT_PAGE
  const navigate = useNavigate()
  const { currentUser } = useCurrentUser()

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

  const redirectWithUrlFilters = (filters: Partial<CollectiveSearchFiltersParams>) => {
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
    finalSearchFilters,
    DEFAULT_COLLECTIVE_TEMPLATE_SEARCH_FILTERS,
    ['venueId', 'offererId']
  )
  //  Admin users are not allowed to check all offers at once or to use the status filter for performance reasons. Unless there is a venue or offerer filter active.
  const isRestrictedAsAdmin = currentUser.isAdmin && !isFilterByVenueOrOfferer

  const collectiveOffersQueryKeys = getCollectiveOffersSwrKeys({
    isNewOffersAndBookingsActive: true,
    isInTemplateOffersPage: true,
    urlSearchFilters: finalSearchFilters,
    selectedOffererId: offererId ?? '',
  })

  const apiFilters: CollectiveSearchFiltersParams = {
    ...DEFAULT_COLLECTIVE_TEMPLATE_SEARCH_FILTERS,
    ...finalSearchFilters,
    ...(isRestrictedAsAdmin ? { status: [] } : {}),
    ...{ offererId: offererId ?? '' },
  }
  delete apiFilters.page

  const offersQuery = useSWR(
    collectiveOffersQueryKeys,
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
    <Layout>
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
    </Layout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = TemplateCollectiveOffers
