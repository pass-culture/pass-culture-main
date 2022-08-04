import { FormikProvider, useFormik } from 'formik'
import React from 'react'
import { useHistory } from 'react-router-dom'

import { TOffererName } from 'core/Offerers/types'
import { createIndividualOffer } from 'core/Offers/adapters'
import {
  IOfferCategory,
  IOfferSubCategory,
  IOfferIndividual,
} from 'core/Offers/types'
import { TOfferIndividualVenue } from 'core/Venue/types'
import { OfferFormLayout } from 'new_components/OfferFormLayout'
import {
  IOfferIndividualFormValues,
  OfferIndividualForm,
  validationSchema,
} from 'new_components/OfferIndividualForm'

import { ActionBar } from '../ActionBar'

import { filterCategories } from './utils'

export interface IInformationsProps {
  offer?: IOfferIndividual
  initialValues: IOfferIndividualFormValues
  offererNames: TOffererName[]
  venueList: TOfferIndividualVenue[]
  categories: IOfferCategory[]
  subCategories: IOfferSubCategory[]
  readOnlyFields?: string[]
}

const Informations = ({
  initialValues,
  offererNames,
  venueList,
  categories,
  subCategories,
  readOnlyFields = [],
}: IInformationsProps): JSX.Element => {
  const history = useHistory()

  const handleNextStep = async () => formik.handleSubmit()

  const onSubmit = async (formValues: IOfferIndividualFormValues) => {
    const { isOk, payload } = await createIndividualOffer(formValues)
    if (isOk) {
      history.push(`/offre/${payload.id}/v3/creation/individuelle/stocks`)
    } else {
      formik.setErrors(payload.errors)
    }
  }

  const formik = useFormik({
    initialValues,
    onSubmit,
    validationSchema,
  })

  const initialVenue: TOfferIndividualVenue | undefined = venueList.find(
    venue => venue.id === initialValues.venueId
  )

  const [filteredCategories, filteredSubCategories] = filterCategories(
    categories,
    subCategories,
    initialVenue
  )

  return (
    <FormikProvider value={formik}>
      <form onSubmit={formik.handleSubmit}>
        <OfferIndividualForm
          offererNames={offererNames}
          venueList={venueList}
          categories={filteredCategories}
          subCategories={filteredSubCategories}
          readOnlyFields={readOnlyFields}
        />

        <OfferFormLayout.ActionBar>
          <ActionBar onClickNext={handleNextStep} />
        </OfferFormLayout.ActionBar>
      </form>
    </FormikProvider>
  )
}

export default Informations
