import {
  FORM_DEFAULT_VALUES,
  IOfferIndividualFormValues,
  setInitialFormValues
} from 'new_components/OfferIndividualForm'

import { Informations as InformationsScreen } from 'screens/OfferIndividual/Informations'
import React from 'react'
import Spinner from 'components/layout/Spinner'
import { createOfferAdapter } from './adapters'
// TODO (rlecellier): rename into getOfferQueryParams
import { queryParamsFromOfferer } from 'components/pages/Offers/utils/queryParamsFromOfferer'
import { useGetOfferIndividualVenues } from 'core/Venue/adapters'
import { useGetOffererNames } from 'core/Offerers/adapters'
import { useHistory } from 'react-router-dom'
import { useHomePath } from 'hooks'
import useNotification from 'components/hooks/useNotification'

const OfferIndividualCreationInformations = (): JSX.Element | null => {
  const homePath = useHomePath()
  const notify = useNotification()
  const history = useHistory()

  const {data: offererNames, isLoading: offererNamesIsLoading, error: offererNamesError} =
    useGetOffererNames()
  const {data: venueList, isLoading: venueListIsLoading, error: venueListError} =
    useGetOfferIndividualVenues()

  const { structure: offererId, lieu: venueId } =
    queryParamsFromOfferer(location)

  if (offererNamesIsLoading || venueListIsLoading) {
    return <Spinner />
  }

  if (offererNamesError || venueListError) {
    notify.error(offererNamesError || venueListError)
    history.push(homePath)

    return null
  }

  const initialValues: IOfferIndividualFormValues = setInitialFormValues(
    FORM_DEFAULT_VALUES,
    offererNames,
    offererId,
    venueId,
    venueList
  )

  return (
    <InformationsScreen
      offererNames={offererNames}
      venueList={venueList}
      createOfferAdapter={createOfferAdapter}
      initialValues={initialValues}
    />
  )
}

export default OfferIndividualCreationInformations
