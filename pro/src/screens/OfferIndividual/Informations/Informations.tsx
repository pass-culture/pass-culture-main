import { FormikProvider, useFormik } from 'formik'
import { IOfferCategory, IOfferSubCategory } from 'core/Offers/types'
import {
  IOfferIndividualFormValues,
  OfferIndividualForm,
  validationSchema,
} from 'new_components/OfferIndividualForm'
import { OFFER_FORM_STEP_IDS, useOfferFormSteps } from 'core/Offers'

import { ActionBar } from '../ActionBar'
import { IOfferIndividual } from 'core/Offers/types'
import { OfferFormLayout } from 'new_components/OfferFormLayout'
import React from 'react'
import { TOfferIndividualVenue } from 'core/Venue/types'
import { TOffererName } from 'core/Offerers/types'
import { fakeOffer } from '../constants'
import { filterCategories } from './utils'
import { useHistory } from 'react-router-dom'

export interface IInformationsProps {
  offer?: IOfferIndividual
  createOfferAdapter: (
    formValues: IOfferIndividualFormValues
  ) => Promise<string | void>
  initialValues: IOfferIndividualFormValues
  offererNames: TOffererName[]
  venueList: TOfferIndividualVenue[]
  categories: IOfferCategory[]
  subCategories: IOfferSubCategory[]
}

const Informations = ({
  offer,
  createOfferAdapter,
  initialValues,
  offererNames,
  venueList,
  categories,
  subCategories,
}: IInformationsProps): JSX.Element => {
  const history = useHistory()

  // call getStep with offer when this screen get it as prop
  const { activeSteps } = useOfferFormSteps(offer)
  const handleNextStep = async () => formik.handleSubmit()

  const onSubmit = async (formValues: IOfferIndividualFormValues) => {
    await createOfferAdapter(formValues)
    // TODO get a real id after offer creation form submit
    history.push(`/offre/${fakeOffer.id}/v3/creation/individuelle/stocks`)
  }

  const { resetForm, ...formik } = useFormik({
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
    <FormikProvider value={{ ...formik, resetForm }}>
      <form onSubmit={formik.handleSubmit}>
        <OfferIndividualForm
          offererNames={offererNames}
          venueList={venueList}
          categories={filteredCategories}
          subCategories={filteredSubCategories}
        />

        <OfferFormLayout.ActionBar>
          <ActionBar
            disableNext={!activeSteps.includes(OFFER_FORM_STEP_IDS.STOCKS)}
            onClickNext={handleNextStep}
          />
        </OfferFormLayout.ActionBar>
      </form>
    </FormikProvider>
  )
}

export default Informations
