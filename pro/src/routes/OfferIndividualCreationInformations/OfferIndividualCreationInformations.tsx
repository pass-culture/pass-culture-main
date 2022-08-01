import React from 'react'
import { useHistory, useParams } from 'react-router-dom'

import useNotification from 'components/hooks/useNotification'
import Spinner from 'components/layout/Spinner'
import { queryParamsFromOfferer } from 'components/pages/Offers/utils/queryParamsFromOfferer'
import { useGetOffererNames } from 'core/Offerers/adapters'
import { useGetCategories, useGetOffer } from 'core/Offers/adapters'
import { useGetOfferIndividualVenues } from 'core/Venue/adapters'
import { useHomePath } from 'hooks'
import useIsLoading from 'hooks/useIsLoading'
import {
  FORM_DEFAULT_VALUES,
  IOfferIndividualFormValues,
  setInitialFormValues,
} from 'new_components/OfferIndividualForm'
import { Informations as InformationsScreen } from 'screens/OfferIndividual/Informations'

import { createOfferAdapter } from './adapters'

// TODO (rlecellier): rename into getOfferQueryParams

const OfferIndividualCreationInformations = (): JSX.Element | null => {
  const { offerId } = useParams<{ offerId?: string }>()
  const homePath = useHomePath()
  const notify = useNotification()
  const history = useHistory()

  const {
    data: offer,
    isLoading: offerIsLoading,
    error: offerError,
  } = useGetOffer(offerId)
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
    isLoading: categoriesIsLoading,
    error: categoriesError,
  } = useGetCategories()

  const isLoading = useIsLoading([
    offererNamesIsLoading,
    offerIsLoading,
    venueListIsLoading,
    categoriesIsLoading,
  ])

  const { structure: offererId, lieu: venueId } =
    queryParamsFromOfferer(location)

  if (
    isLoading ||
    offererNamesIsLoading === true ||
    venueListIsLoading === true ||
    categoriesIsLoading === true ||
    offerIsLoading === true
  ) {
    return <Spinner />
  }

  if (
    offererNamesError ||
    venueListError ||
    categoriesError ||
    (offerId && offerError)
  ) {
    const loadingError = [
      offererNamesError,
      venueListError,
      categoriesError,
      offerError,
    ].find(error => error !== undefined)
    if (loadingError !== undefined) {
      notify.error(loadingError.message)
      history.push(homePath)
    }
    return null
  }

  const { categories, subCategories } = categoriesData

  // TODO: prefill informations from previously saved offer
  const initialValues: IOfferIndividualFormValues = setInitialFormValues(
    FORM_DEFAULT_VALUES,
    offererNames,
    offererId,
    venueId,
    venueList
  )

  return (
    <InformationsScreen
      offer={offer || undefined}
      offererNames={offererNames}
      categories={categories}
      subCategories={subCategories}
      venueList={venueList}
      createOfferAdapter={createOfferAdapter}
      initialValues={initialValues}
    />
  )
}

export default OfferIndividualCreationInformations
