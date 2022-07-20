import React from 'react'
import { useHistory } from 'react-router-dom'

import useNotification from 'components/hooks/useNotification'
import Spinner from 'components/layout/Spinner'
import { queryParamsFromOfferer } from 'components/pages/Offers/utils/queryParamsFromOfferer'
import { useGetOffererNames } from 'core/Offerers/adapters'
import { useGetCategories } from 'core/Offers/adapters'
import { IOfferIndividual } from 'core/Offers/types'
import { useGetOfferIndividualVenues } from 'core/Venue/adapters'
import { useHomePath } from 'hooks'
import {
  FORM_DEFAULT_VALUES,
  IOfferIndividualFormValues,
  setDefaultInitialFormValues,
} from 'new_components/OfferIndividualForm'
import { Informations as InformationsScreen } from 'screens/OfferIndividual/Informations'

interface IOfferIndividualCreationInformationsProps {
  offer?: IOfferIndividual
}

const OfferIndividualCreationInformations = ({
  offer,
}: IOfferIndividualCreationInformationsProps): JSX.Element | null => {
  const homePath = useHomePath()
  const notify = useNotification()
  const history = useHistory()

  const {
    data: offererNames,
    isLoading: offererNamesIsLoading,
    error: offererNamesError,
  } = useGetOffererNames()
  const {
    data: venueList,
    isLoading: venueListIsLoading,
    error: venueListError,
  } = useGetOfferIndividualVenues()
  const {
    data: categoriesData,
    isLoading: categoriesStatus,
    error: categoriesError,
  } = useGetCategories()

  const { structure: offererId, lieu: venueId } =
    queryParamsFromOfferer(location)

  if (
    offererNamesIsLoading === true ||
    venueListIsLoading === true ||
    categoriesStatus === true
  ) {
    return <Spinner />
  }

  if (offererNamesError || venueListError || categoriesError) {
    const loadingError = [
      offererNamesError,
      venueListError,
      categoriesError,
    ].find(error => error !== undefined)
    if (loadingError !== undefined) {
      notify.error(loadingError.message)
      history.push(homePath)
    }
    return null
  }

  const { categories, subCategories } = categoriesData

  // TODO: prefill informations from previously saved offer
  const initialValues: IOfferIndividualFormValues = setDefaultInitialFormValues(
    FORM_DEFAULT_VALUES,
    offererNames,
    offererId,
    venueId,
    venueList
  )

  return (
    <InformationsScreen
      offer={offer}
      offererNames={offererNames}
      categories={categories}
      subCategories={subCategories}
      venueList={venueList}
      initialValues={initialValues}
    />
  )
}

export default OfferIndividualCreationInformations
