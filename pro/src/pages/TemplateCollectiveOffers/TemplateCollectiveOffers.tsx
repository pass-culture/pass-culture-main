import { useSelector } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import { CollectiveOfferType } from 'apiClient/v1'
import { Layout } from 'app/App/layout/Layout'
import {
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
import { serializeApiCollectiveFilters } from 'commons/core/Offers/utils/serializer'
import { useOfferer } from 'commons/hooks/swr/useOfferer'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { selectCurrentOffererId } from 'commons/store/offerer/selectors'
import { getStoredFilterConfig } from 'components/OffersTable/OffersTableSearch/utils'
import { TemplateCollectiveOffersScreen } from 'pages/TemplateCollectiveOffers/TemplateCollectiveOffersScreen/TemplateCollectiveOffersScreen'
import { formatAndOrderVenues } from 'repository/venuesService'
import { Spinner } from 'ui-kit/Spinner/Spinner'

export const TemplateCollectiveOffers = (): JSX.Element => {
  const isToggleAndMemorizeFiltersEnabled = useActiveFeature(
    'WIP_COLLAPSED_MEMORIZED_FILTERS'
  )
  const urlSearchFilters = useQueryCollectiveSearchFilters()
  const { storedFilters } = getStoredFilterConfig('template')
  const finalSearchFilters = {
    ...urlSearchFilters,
    ...(isToggleAndMemorizeFiltersEnabled
      ? (storedFilters as Partial<CollectiveSearchFiltersParams>)
      : {}),
  }
  const offererId = useSelector(selectCurrentOffererId)?.toString()

  const currentPageNumber = finalSearchFilters.page ?? DEFAULT_PAGE
  const navigate = useNavigate()

  const { data: offerer } = useOfferer(
    offererId !== DEFAULT_COLLECTIVE_TEMPLATE_SEARCH_FILTERS.offererId ? offererId : null,
    true
  )

  const { data } = useSWR(
    [GET_VENUES_QUERY_KEY, offerer?.id],
    ([, offererIdParam]) => api.getVenues(null, null, offererIdParam),
    { fallbackData: { venues: [] } }
  )
  const venues = formatAndOrderVenues(data.venues)

  const redirectWithUrlFilters = (
    filters: Partial<CollectiveSearchFiltersParams>
  ) => {
    // We dont need to pass the offererId in the URL since
    // its already present in the redux store (useSelector(selectCurrentOffererId))
    delete filters.offererId

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
      const {
        nameOrIsbn,
        offererId,
        venueId,
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
        creationMode,
        periodBeginningDate,
        periodEndingDate,
        CollectiveOfferType.TEMPLATE,
        format
      )
    },
    { fallbackData: [] }
  )

  if (offersQuery.isLoading) {
    return <Layout>
      <Spinner />
    </Layout>
  }

  return (
    <Layout mainHeading='Offres vitrines'>
      <TemplateCollectiveOffersScreen
        currentPageNumber={currentPageNumber}
        initialSearchFilters={apiFilters}
        isLoading={offersQuery.isLoading}
        offerer={offerer}
        offers={offersQuery.data}
        redirectWithUrlFilters={redirectWithUrlFilters}
        urlSearchFilters={urlSearchFilters}
        venues={venues}
      />
    </Layout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = TemplateCollectiveOffers
