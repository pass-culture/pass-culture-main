import React from 'react'
import { useNavigate, useParams } from 'react-router-dom'

import { setDefaultInitialFormValues } from 'components/VenueForm'
import useGetOfferer from 'core/Offerers/getOffererAdapter/useGetOfferer'
import { useGetVenueLabels } from 'core/Venue/adapters/getVenueLabelsAdapter'
import { useGetVenueTypes } from 'core/Venue/adapters/getVenueTypeAdapter'
import useNotification from 'hooks/useNotification'
import { VenueFormScreen } from 'screens/VenueForm'
import Spinner from 'ui-kit/Spinner/Spinner'

const VenueCreation = (): JSX.Element | null => {
  const homePath = '/accueil'
  const { offererId } = useParams<{ offererId: string }>()
  const notify = useNotification()
  const navigate = useNavigate()

  const initialValues = setDefaultInitialFormValues()

  const {
    isLoading: isLoadingOfferer,
    error: errorOfferer,
    data: offerer,
  } = useGetOfferer(offererId)
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

  if (isLoadingOfferer || isLoadingVenueTypes || isLoadingVenueLabels) {
    return <Spinner />
  }

  if (errorOfferer || errorVenueTypes || errorVenueLabels) {
    const loadingError = [errorOfferer, errorVenueTypes, errorVenueLabels].find(
      error => error !== undefined
    )
    if (loadingError !== undefined) {
      navigate(homePath)
      notify.error(loadingError.message)
    }
    return null
  }

  return (
    <VenueFormScreen
      initialValues={initialValues}
      isCreatingVenue
      offerer={offerer}
      venueTypes={venueTypes}
      venueLabels={venueLabels}
    />
  )
}

export default VenueCreation
