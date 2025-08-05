import { useSelector } from 'react-redux'
import { useNavigate } from 'react-router'
import { formatAndOrderVenues } from 'repository/venuesService'
import useSWR from 'swr'

import { api } from '@/apiClient/api'
import { CollectiveOfferType } from '@/apiClient/v1'
import { Layout } from '@/app/App/layout/Layout'
import { GET_VENUES_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { DEFAULT_PAGE } from '@/commons/core/Offers/constants'
import { useDefaultCollectiveSearchFilters } from '@/commons/core/Offers/hooks/useDefaultCollectiveSearchFilters'
import { useQueryCollectiveSearchFilters } from '@/commons/core/Offers/hooks/useQuerySearchFilters'
import { CollectiveSearchFiltersParams } from '@/commons/core/Offers/types'
import { computeCollectiveOffersUrl } from '@/commons/core/Offers/utils/computeCollectiveOffersUrl'
import { getCollectiveOffersSwrKeys } from '@/commons/core/Offers/utils/getCollectiveOffersSwrKeys'
import { serializeApiCollectiveFilters } from '@/commons/core/Offers/utils/serializer'
import { useOfferer } from '@/commons/hooks/swr/useOfferer'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { selectCurrentOffererId } from '@/commons/store/offerer/selectors'
import { getStoredFilterConfig } from '@/components/OffersTable/OffersTableSearch/utils'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

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
  const offererId = useSelector(selectCurrentOffererId)?.toString()

  const defaultCollectiveFilters = useDefaultCollectiveSearchFilters()

  const currentPageNumber = finalSearchFilters.page ?? DEFAULT_PAGE

  const {
    data: offerer,
    isLoading: isOffererLoading,
    isValidating: isOffererValidating,
  } = useOfferer(
    offererId !== defaultCollectiveFilters.offererId ? offererId : null,
    true
  )

  const {
    data,
    isLoading: isVenuesLoading,
    isValidating: isVenuesValidating,
  } = useSWR(
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

    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    navigate(computeCollectiveOffersUrl(filters, defaultCollectiveFilters), {
      replace: true,
    })
  }

  const collectiveOffersQueryKeys = getCollectiveOffersSwrKeys({
    isNewOffersAndBookingsActive,
    isInTemplateOffersPage: false,
    urlSearchFilters: finalSearchFilters,
    selectedOffererId: offererId ?? '',
  })

  const apiFilters: CollectiveSearchFiltersParams = {
    ...defaultCollectiveFilters,
    ...finalSearchFilters,
    ...{ offererId: offererId?.toString() ?? 'all' },
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
        collectiveOfferType,
        format,
      } = serializeApiCollectiveFilters(apiFilters, defaultCollectiveFilters)

      return api.getCollectiveOffers(
        nameOrIsbn,
        offererId,
        status,
        venueId,
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
    <Layout mainHeading="Offres collectives">
      {/* When the venues are cached for a given offerer, we still need to reset the Screen component.
      SWR isLoading is only true when the data is not cached, while isValidating is always set to true when the key is updated */}
      {isOffererLoading ||
      isOffererValidating ||
      isVenuesLoading ||
      isVenuesValidating ? (
        <Spinner />
      ) : (
        <CollectiveOffersScreen
          currentPageNumber={currentPageNumber}
          initialSearchFilters={apiFilters}
          isLoading={offersQuery.isLoading}
          offerer={offerer}
          offers={offersQuery.data}
          redirectWithUrlFilters={redirectWithUrlFilters}
          urlSearchFilters={urlSearchFilters}
          venues={venues}
        />
      )}
    </Layout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = CollectiveOffers
