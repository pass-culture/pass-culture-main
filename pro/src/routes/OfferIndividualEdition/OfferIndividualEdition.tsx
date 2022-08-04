import React from 'react'
import { useHistory, useParams } from 'react-router-dom'

import useNotification from 'components/hooks/useNotification'
import Spinner from 'components/layout/Spinner'
import Titles from 'components/layout/Titles/Titles'
import { useHomePath } from 'hooks'
import {
  setFormReadOnlyFields,
  IOfferIndividualFormValues,
  setInitialFormValues,
} from 'new_components/OfferIndividualForm'
import { Informations as InformationsScreen } from 'screens/OfferIndividual/Informations'

import { useGetData } from './hooks'

const OfferIndividualEdition = (): JSX.Element | null => {
  const { offerId } = useParams<{ offerId: string }>()
  const homePath = useHomePath()
  const notify = useNotification()
  const history = useHistory()

  const { data, isLoading, loadingError } = useGetData(offerId)

  if (isLoading === true) return <Spinner />
  if (loadingError !== undefined) {
    notify.error(loadingError)
    history.push(homePath)
    return null
  }

  const {
    offer,
    venueList,
    offererNames,
    categoriesData: { categories, subCategories },
  } = data

  const initialValues: IOfferIndividualFormValues = setInitialFormValues(
    offer,
    subCategories
  )

  const readOnlyFields = setFormReadOnlyFields(offer)

  return (
    <>
      <Titles title="Editez votre offre" />
      <InformationsScreen
        readOnlyFields={readOnlyFields}
        offererNames={offererNames}
        categories={categories}
        subCategories={subCategories}
        venueList={venueList}
        initialValues={initialValues}
      />
    </>
  )
}

export default OfferIndividualEdition
