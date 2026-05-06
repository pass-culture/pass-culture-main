import { useEffect } from 'react'
import { useNavigate } from 'react-router'
import useSWR from 'swr'

import { apiNew } from '@/apiClient/api'
import { GetVenueAddressesWithOffersOption } from '@/apiClient/v1/new'
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
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { sortByLabel } from '@/commons/utils/strings'
import { useStoredFilterConfig } from '@/components/OffersTableSearch/utils'

import type { IndividualOffersFilters } from './common/types'
import { IndividualOffersContainer } from './IndividualOffersContainer/IndividualOffersContainer'
import { computeIndividualApiFilters } from './utils/computeIndividualApiFilters'

export const IndividualOffers = () => {
  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)
  const snackbar = useSnackBar()

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
    () => apiNew.getCategories(),
    { fallbackData: { categories: [], subcategories: [] } }
  )

  const categoriesOptions = sortByLabel(
    (categoriesQuery.data?.categories ?? [])
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
    // TODO (igabriele, 2026-05-07): Delete this line once `offererId` is removed and `venueId` made mandatory in `ListOffersQueryModel`
    delete filters.offererId

    navigate(computeIndividualOffersUrl(filters), { replace: true })
  }

  const venueAddressQuery = useVenueAddresses(
    GetVenueAddressesWithOffersOption.INDIVIDUAL_OFFERS_ONLY
  )
  const venueAddresses = formatAndOrderAddresses(venueAddressQuery.data ?? [])

  const apiFilters = computeIndividualApiFilters(
    finalSearchFilters,
    selectedPartnerVenue.managingOfferer.id
  )

  const offersQuery = useSWR([GET_OFFERS_QUERY_KEY, apiFilters], () =>
    apiNew.listOffers({ query: apiFilters })
  )

  useEffect(() => {
    if (offersQuery.error) {
      snackbar.error(
        'Une erreur est survenue pendant le rafraîchissement des offres.'
      )
    }
  }, [offersQuery.error, snackbar.error])

  return (
    <>
      <MainHeading mainHeading="Offres individuelles" />

      <HeadlineOfferContextProvider>
        <IndividualOffersContainer
          categories={categoriesOptions}
          currentPageNumber={currentPageNumber}
          initialSearchFilters={apiFilters}
          isLoading={offersQuery.isLoading}
          offers={offersQuery.data}
          redirectWithSelectedFilters={redirectWithSelectedFilters}
          venueAddresses={venueAddresses}
        />
      </HeadlineOfferContextProvider>
    </>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = IndividualOffers
