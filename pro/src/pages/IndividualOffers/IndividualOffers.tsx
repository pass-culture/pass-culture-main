import { useSelector } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import { Layout } from 'app/App/layout/Layout'
import {
  GET_CATEGORIES_QUERY_KEY,
  GET_OFFERER_ADDRESS_QUERY_KEY,
  GET_OFFERS_QUERY_KEY,
  GET_VENUES_QUERY_KEY,
} from 'commons/config/swrQueryKeys'
import { HeadlineOfferContextProvider } from 'commons/context/HeadlineOfferContext/HeadlineOfferContext'
import { DEFAULT_PAGE } from 'commons/core/Offers/constants'
import { useQuerySearchFilters } from 'commons/core/Offers/hooks/useQuerySearchFilters'
import { SearchFiltersParams } from 'commons/core/Offers/types'
import { computeIndividualOffersUrl } from 'commons/core/Offers/utils/computeIndividualOffersUrl'
import { serializeApiFilters } from 'commons/core/Offers/utils/serializer'
import { Audience } from 'commons/core/shared/types'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { selectCurrentOffererId } from 'commons/store/offerer/selectors'
import { sortByLabel } from 'commons/utils/strings'
import { HeadlineOfferBanner } from 'components/HeadlineOfferBanner/HeadlineOfferBanner'
import { getStoredFilterConfig } from 'components/OffersTable/OffersTableSearch/utils'
import {
  formatAndOrderAddresses,
  formatAndOrderVenues,
} from 'repository/venuesService'
import { Spinner } from 'ui-kit/Spinner/Spinner'

import { IndividualOffersContainer } from './IndividualOffersContainer/IndividualOffersContainer'
import { computeIndividualApiFilters } from './utils/computeIndividualApiFilters'

export const IndividualOffers = (): JSX.Element => {
  const isToggleAndMemorizeFiltersEnabled = useActiveFeature(
    'WIP_COLLAPSED_MEMORIZED_FILTERS'
  )
  const urlSearchFilters = useQuerySearchFilters()
  const { storedFilters } = getStoredFilterConfig('individual')
  const finalSearchFilters = {
    ...urlSearchFilters,
    ...(isToggleAndMemorizeFiltersEnabled
      ? (storedFilters as Partial<SearchFiltersParams>)
      : {}),
  }

  const currentPageNumber = finalSearchFilters.page ?? DEFAULT_PAGE
  const navigate = useNavigate()
  const selectedOffererId = useSelector(selectCurrentOffererId)
  const isOfferAddressEnabled = useActiveFeature('WIP_ENABLE_OFFER_ADDRESS')

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

  const redirectWithSelectedFilters = (
    filters: Partial<SearchFiltersParams> & { audience?: Audience }
  ) => {
    // We dont need to pass the offererId in the URL since
    // its already present in the redux store (useSelector(selectCurrentOffererId))
    delete filters.offererId

    navigate(computeIndividualOffersUrl(filters), { replace: true })
  }

  const {
    data,
    isLoading: isLoadingVenues,
    //  When the venues are cached for a given offerer, we still need to reset the Screen component.
    //  SWR isLoading is only true when the data is not cached, while isValidating is always set to true when the key is updated
    isValidating: isValidatingVenues,
  } = useSWR([GET_VENUES_QUERY_KEY, selectedOffererId], () =>
    api.getVenues(null, null, selectedOffererId)
  )
  const venues = formatAndOrderVenues(data?.venues ?? [])

  const offererAddressQuery = useSWR(
    selectedOffererId && isOfferAddressEnabled
      ? [GET_OFFERER_ADDRESS_QUERY_KEY, selectedOffererId]
      : null,
    ([, offererIdParam]) => api.getOffererAddresses(offererIdParam, true),
    { fallbackData: [] }
  )
  const offererAddresses = formatAndOrderAddresses(offererAddressQuery.data)

  const apiFilters = computeIndividualApiFilters(
    finalSearchFilters,
    selectedOffererId?.toString()
  )

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

  const offers = offersQuery.error ? [] : offersQuery.data || []

  return (
    <HeadlineOfferContextProvider>
      <Layout
        mainHeading="Offres individuelles"
        mainBanner={<HeadlineOfferBanner />}
      >
        {isLoadingVenues || isValidatingVenues ? (
          <Spinner />
        ) : (
          <IndividualOffersContainer
            categories={categoriesOptions}
            currentPageNumber={currentPageNumber}
            initialSearchFilters={apiFilters}
            isLoading={offersQuery.isLoading}
            offers={offers}
            redirectWithSelectedFilters={redirectWithSelectedFilters}
            venues={venues}
            offererAddresses={offererAddresses}
          />
        )}
      </Layout>
    </HeadlineOfferContextProvider>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = IndividualOffers
