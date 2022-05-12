import React from 'react'
import { useHistory } from 'react-router-dom'

import useNotification from 'components/hooks/useNotification'
// TODO (rlecellier): rename into getOfferQueryParams
import { queryParamsFromOfferer } from 'components/pages/Offers/utils/queryParamsFromOfferer'
import { useHomePath } from 'hooks'

import Spinner from 'components/layout/Spinner'
import {
  FORM_DEFAULT_VALUES,
  IOfferIndividualFormValues,
  setInitialFormValues,
} from 'new_components/OfferIndividualForm'
import { Informations as InformationsScreen } from 'screens/OfferIndividual/Informations'

import { createOfferAdapter } from './adapters'
import { useOffererNames, useOfferIndividualVenues } from './hooks'

const OfferIndividualCreationInformations = (): JSX.Element | null => {
  const homePath = useHomePath()
  const notify = useNotification()
  const history = useHistory()
  const {
    offererNames,
    isLoading: isOffererLoading,
    error: offererError,
  } = useOffererNames()
  const {
    offerIndividualVenues: venueList,
    isLoading: isVenueLoading,
    error: venueError,
  } = useOfferIndividualVenues()

  const { structure: offererId, lieu: venueId } =
    queryParamsFromOfferer(location)

  const hasError = offererError || venueError
  const isReady = !isOffererLoading && !isVenueLoading
  let initialValues: IOfferIndividualFormValues = FORM_DEFAULT_VALUES

  if (hasError) {
    notify.error(offererError || venueError)
    history.push(homePath)
  } else if (isReady) {
    initialValues = setInitialFormValues(
      initialValues,
      offererNames,
      offererId,
      venueId,
      venueList
    )
  }

  return (
    <>
      {isReady ? (
        <InformationsScreen
          offererNames={offererNames}
          venueList={venueList}
          createOfferAdapter={createOfferAdapter}
          initialValues={initialValues}
        />
      ) : (
        <Spinner />
      )}
    </>
  )
}

export default OfferIndividualCreationInformations
