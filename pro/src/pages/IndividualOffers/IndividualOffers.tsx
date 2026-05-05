import { useNavigate } from 'react-router'
import useSWR from 'swr'

import { api, apiNew } from '@/apiClient/api'
import { GetVenueAddressesWithOffersOption } from '@/apiClient/v1'
import { MainHeading } from '@/app/App/layouts/components/MainHeading/MainHeading'
import {
  GET_CATEGORIES_QUERY_KEY,
  GET_OFFERS_QUERY_KEY,
} from '@/commons/config/swrQueryKeys'
import { HeadlineOfferContextProvider } from '@/commons/context/HeadlineOfferContext/HeadlineOfferContext'
import { DEFAULT_PAGE } from '@/commons/core/Offers/constants'
import { useQuerySearchFilters } from '@/commons/core/Offers/hooks/useQuerySearchFilters'
import { computeIndividualOffersUrl } from '@/commons/core/Offers/utils/computeIndividualOffersUrl'
import type { Audience } from '@/commons/core/shared/types'
import { formatAndOrderAddresses } from '@/commons/format/venuesService'
import { useVenueAddresses } from '@/commons/hooks/swr/useVenueAddresses'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useGracefulSwrResponse } from '@/commons/hooks/useGracefulSwrResponse'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { sortByLabel } from '@/commons/utils/strings'
import { useStoredFilterConfig } from '@/components/OffersTableSearch/utils'

import type { IndividualOffersFilters } from './common/types'
import { IndividualOffersContainer } from './IndividualOffersContainer/IndividualOffersContainer'
import { computeIndividualApiFilters } from './utils/computeIndividualApiFilters'

export const IndividualOffers = () => {
  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)

  const urlSearchFilters = useQuerySearchFilters()
  const { storedFilters } = useStoredFilterConfig('individual')
  const finalSearchFilters = {
    ...urlSearchFilters,
    ...(storedFilters as Partial<IndividualOffersFilters>),
    venueId: selectedPartnerVenue.id,
  }

  const currentPageNumber = finalSearchFilters.page ?? DEFAULT_PAGE
  const navigate = useNavigate()

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
    filters: Partial<IndividualOffersFilters> & {
      audience?: Audience
    }
  ) => {
    // We dont need to pass the offererId in the URL since
    // its already present in the redux store (useSelector(selectCurrentOfferer))
    delete filters.offererId

    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    navigate(computeIndividualOffersUrl(filters), { replace: true })
  }

  const venueAddressQuery = useVenueAddresses(
    GetVenueAddressesWithOffersOption.INDIVIDUAL_OFFERS_ONLY
  )
  const offererAddresses = formatAndOrderAddresses(venueAddressQuery.data)

  const apiFilters = computeIndividualApiFilters(
    finalSearchFilters,
    selectedPartnerVenue.managingOfferer.id
  )

  const offersQuery = useSWR([GET_OFFERS_QUERY_KEY, apiFilters], () =>
    apiNew.listOffers({ query: apiFilters })
  )

  const offersResponse = useGracefulSwrResponse(
    offersQuery,
    'Une erreur est survenue pendant le rafraîchissement des offres.'
  )
  if (offersResponse.hasFirstLoadError) {
    return (
      <>
        <MainHeading mainHeading="Offres individuelles" />
        <p>Nous n'avons pas pu récupérer la liste des offres.</p>
      </>
    )
  }

  return (
    <>
      <MainHeading mainHeading="Offres individuelles" />

      <HeadlineOfferContextProvider>
        <IndividualOffersContainer
          categories={categoriesOptions}
          currentPageNumber={currentPageNumber}
          initialSearchFilters={apiFilters}
          isLoading={offersResponse.isFirstLoading}
          offers={offersResponse.data}
          redirectWithSelectedFilters={redirectWithSelectedFilters}
          offererAddresses={offererAddresses}
        />
      </HeadlineOfferContextProvider>
    </>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = IndividualOffers
