import { FormikProvider, useFormik } from 'formik'
import { OFFER_FORM_STEP_IDS, useOfferFormSteps } from 'core/Offers'

import { ActionBar } from '../ActionBar'
import { OfferFormLayout } from 'new_components/OfferFormLayout'
import React from 'react'
import { fakeOffer } from '../constants'
import { useHistory } from 'react-router-dom'

const Stocks = (): JSX.Element => {
  const history = useHistory()
  // call getStep with offer when this screen get it as prop
  const { activeSteps } = useOfferFormSteps(fakeOffer)

  const handleNextStep = () => {
    // TODO get offerId from url query string
    history.push(
      `/offre/${fakeOffer.id}/v3/creation/individuelle/recapitulatif`
    )
  }
  const handlePreviousStep = () => {
    // TODO get offerId from url query string
    const testCreatedOfferId = 'AL4Q'
    history.push(
      `/offre/${testCreatedOfferId}/v3/creation/individuelle/informations`
    )
  }

  const initialValues = {}
  const onSubmit = () => {
    // TODO stock submit
  }
  const validationSchema = {}

  const { resetForm, ...formik } = useFormik({
    initialValues,
    onSubmit,
    validationSchema,
  })

  return (
    <FormikProvider value={{ ...formik, resetForm }}>
      <h2>Stock & Prix</h2>

      <form onSubmit={formik.handleSubmit}>
        <p> TODO stock form </p>

        <OfferFormLayout.ActionBar>
          <ActionBar
            disableNext={!activeSteps.includes(OFFER_FORM_STEP_IDS.SUMMARY)}
            onClickNext={handleNextStep}
            onClickPrevious={handlePreviousStep}
          />
        </OfferFormLayout.ActionBar>
      </form>
    </FormikProvider>
  )
}

export default Stocks
