import React from 'react'
import { useNavigate, useParams } from 'react-router-dom'

import { OfferStatus } from 'apiClient/v1'
import { setInitialFormValues } from 'components/VenueForm'
import useGetOfferer from 'core/Offerers/getOffererAdapter/useGetOfferer'
import { DEFAULT_SEARCH_FILTERS } from 'core/Offers'
import { useGetVenue } from 'core/Venue'
import { useGetVenueLabels } from 'core/Venue/adapters/getVenueLabelsAdapter'
import { useGetVenueTypes } from 'core/Venue/adapters/getVenueTypeAdapter'
import { useHomePath } from 'hooks'
import useNotification from 'hooks/useNotification'
import useGetFilteredOffersAdapter from 'pages/Offers/adapters/useGetFilteredOffers'
import { VenueFormScreen } from 'screens/VenueForm'
import Spinner from 'ui-kit/Spinner/Spinner'

import useGetProviders from '../../core/Venue/adapters/getProviderAdapter/useGetProvider'
import useGetVenueProviders from '../../core/Venue/adapters/getVenueProviderAdapter/useGetVenueProvider'

const VenueEdition = (): JSX.Element | null => {
  const homePath = useHomePath()
  const navigate = useNavigate()
  const { offererId, venueId } = useParams<{
    offererId: string
    venueId: string
  }>()
  const notify = useNotification()
  const {
    isLoading: isLoadingVenue,
    error: errorVenue,
    data: venue,
  } = useGetVenue(venueId)
  const {
    isLoading: isLoadingVenueTypes,
    error: errorVenueTypes,
    data: venueTypes,
  } = useGetVenueTypes()
  const {
    isLoading: isLoadingVenueLabels,
    error: errorVenueLabels,
    data: venueLabels,
  } = useGetVenueLabels()
  const {
    isLoading: isLoadingOfferer,
    error: errorOfferer,
    data: offerer,
  } = useGetOfferer(offererId)
  const {
    isLoading: isLoadingProviders,
    error: errorProviders,
    data: providers,
  } = useGetProviders(venueId)
  const {
    isLoading: isLoadingVenueProviders,
    error: errorVenueProviders,
    data: venueProviders,
  } = useGetVenueProviders(venueId)

  const apiFilters = {
    ...DEFAULT_SEARCH_FILTERS,
    status: OfferStatus.ACTIVE,
    venueId: venue?.id ?? '',
  }

  const {
    isLoading: isLoadingVenueOffers,
    error: errorVenueOffers,
    data: venueOffers,
  } = useGetFilteredOffersAdapter(apiFilters)

  const hasBookingQuantity = venueOffers?.offers.some(offer => {
    return offer.stocks.some(stock => {
      const currentBookingQuantity = stock?.bookingQuantity
      if (currentBookingQuantity && currentBookingQuantity > 0) {
        return true
      }
      return false
    })
  })

  if (
    isLoadingVenue ||
    isLoadingVenueTypes ||
    isLoadingVenueLabels ||
    isLoadingProviders ||
    isLoadingVenueProviders ||
    isLoadingOfferer ||
    isLoadingVenueOffers
  ) {
    return <Spinner />
  }

  if (
    errorOfferer ||
    errorVenue ||
    errorVenueTypes ||
    errorVenueLabels ||
    errorVenueProviders ||
    errorProviders ||
    errorVenueOffers
  ) {
    const loadingError = [
      errorOfferer,
      errorVenue,
      errorVenueTypes,
      errorVenueLabels,
    ].find(error => error !== undefined)
    if (loadingError !== undefined) {
      navigate(homePath)
      notify.error(loadingError.message)
      return null
    }
    return null
  }

  const initialValues = setInitialFormValues(venue)
  return (
    <VenueFormScreen
      initialValues={initialValues}
      isCreatingVenue={false}
      offerer={offerer}
      venueTypes={venueTypes}
      venueLabels={venueLabels}
      providers={providers}
      venue={venue}
      venueProviders={venueProviders}
    />
  )
}

export default VenueEdition
