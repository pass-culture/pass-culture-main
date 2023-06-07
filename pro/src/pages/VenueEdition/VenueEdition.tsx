import React from 'react'
import { useNavigate, useParams } from 'react-router-dom'

import { OfferStatus } from 'apiClient/v1'
import { setInitialFormValues } from 'components/VenueForm'
import useGetOfferer from 'core/Offerers/getOffererAdapter/useGetOfferer'
import { DEFAULT_SEARCH_FILTERS } from 'core/Offers'
import { useGetVenue } from 'core/Venue'
import { useGetVenueLabels } from 'core/Venue/adapters/getVenueLabelsAdapter'
import { useGetVenueTypes } from 'core/Venue/adapters/getVenueTypeAdapter'
import { useAdapter } from 'hooks'
import useNotification from 'hooks/useNotification'
import {
  getFilteredOffersAdapter,
  Payload,
} from 'pages/Offers/adapters/getFilteredOffersAdapter'
import { VenueFormScreen } from 'screens/VenueForm'
import Spinner from 'ui-kit/Spinner/Spinner'

import useGetProviders from '../../core/Venue/adapters/getProviderAdapter/useGetProvider'
import useGetVenueProviders from '../../core/Venue/adapters/getVenueProviderAdapter/useGetVenueProvider'

import { offerHasBookingQuantity } from './utils'

const VenueEdition = (): JSX.Element | null => {
  const homePath = '/accueil'
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
  } = useGetVenue(Number(venueId))
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
  } = useGetProviders(Number(venueId))
  const {
    isLoading: isLoadingVenueProviders,
    error: errorVenueProviders,
    data: venueProviders,
  } = useGetVenueProviders(Number(venueId))

  const apiFilters = {
    ...DEFAULT_SEARCH_FILTERS,
    status: OfferStatus.ACTIVE,
    venueId: venue?.id ?? '',
  }

  const { isLoading: isLoadingVenueOffers, data: venueOffers } = useAdapter<
    Payload,
    Payload
  >(() => getFilteredOffersAdapter(apiFilters))

  const hasBookingQuantity = offerHasBookingQuantity(venueOffers?.offers)

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
    errorProviders
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
    /* istanbul ignore next: Never */
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
      hasBookingQuantity={venue?.id ? hasBookingQuantity : false}
    />
  )
}

export default VenueEdition
