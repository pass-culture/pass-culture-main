import React from 'react'
import { useHistory, useParams } from 'react-router'

import useNotification from 'components/hooks/useNotification'
import Spinner from 'components/layout/Spinner'
import useGetOfferer from 'core/Offerers/getOffererAdapter/useGetOfferer'
import { useGetVenueLabels } from 'core/Venue/adapters/getVenueLabelsAdapter'
import { useGetVenueTypes } from 'core/Venue/adapters/getVenueTypeAdapter'
import { useHomePath } from 'hooks'
import { setDefaultInitialFormValues } from 'new_components/VenueForm'
import { VenueFormScreen } from 'screens/VenueForm'

const VenueCreation = (): JSX.Element | null => {
  const homePath = useHomePath()
  const { offererId } = useParams<{ offererId: string }>()
  const notify = useNotification()
  const history = useHistory()

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
      notify.error(loadingError.message)
      history.push(homePath)
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
