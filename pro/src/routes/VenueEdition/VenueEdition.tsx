import React from 'react'
import { useHistory, useParams } from 'react-router'

import useNotification from 'components/hooks/useNotification'
import Spinner from 'components/layout/Spinner'
import useGetOfferer from 'core/Offerers/getOffererAdapter/useGetOfferer'
import { useGetVenue } from 'core/Venue'
import { useGetVenueLabels } from 'core/Venue/adapters/getVenueLabelsAdapter'
import { useGetVenueTypes } from 'core/Venue/adapters/getVenueTypeAdapter'
import { useHomePath } from 'hooks'
import { setInitialFormValues } from 'new_components/VenueForm'
import { VenueFormScreen } from 'screens/VenueForm'

import useGetProviders from '../../core/Venue/adapters/getProviderAdapter/useGetProvider'
import useGetVenueProviders from '../../core/Venue/adapters/getVenueProviderAdapter/useGetVenueProvider'

const VenueEdition = (): JSX.Element | null => {
  const homePath = useHomePath()
  const { offererId } = useParams<{ offererId: string }>()
  const { venueId } = useParams<{ venueId: string }>()
  const notify = useNotification()
  const history = useHistory()
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
  if (
    isLoadingVenue ||
    isLoadingVenueTypes ||
    isLoadingVenueLabels ||
    isLoadingProviders ||
    isLoadingVenueProviders ||
    isLoadingOfferer
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
      notify.error(loadingError.message)
      history.push(homePath)
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
