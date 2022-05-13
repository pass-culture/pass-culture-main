import Breadcrumb, { BreadcrumbStyle } from 'new_components/Breadcrumb'
import { FormikProvider, useFormik } from 'formik'
import { OFFER_FORM_STEP_IDS, fakeOffer } from '../constants'

import { ActionBar } from '../ActionBar'
import { OfferFormLayout } from 'new_components/OfferFormLayout'
import React from 'react'
import { getStepsOffer } from '../utils/steps'
import { useHistory } from 'react-router-dom'

const Stocks = (): JSX.Element => {
  const history = useHistory()
  // call getStep with offer when this screen get it as prop
  const { stepList, activeSteps } = getStepsOffer(fakeOffer)

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
    <OfferFormLayout>
      <OfferFormLayout.TitleBlock>
        <h1>Créer une offe</h1>
      </OfferFormLayout.TitleBlock>

      <OfferFormLayout.Stepper>
        <Breadcrumb
          activeStep={OFFER_FORM_STEP_IDS.STOCKS}
          steps={Object.values(stepList)}
          styleType={BreadcrumbStyle.TAB}
        />
      </OfferFormLayout.Stepper>

      <OfferFormLayout.Content>
        <h2>Stock & Prix</h2>

        <FormikProvider value={{ ...formik, resetForm }}>
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
      </OfferFormLayout.Content>
    </OfferFormLayout>
  )
}

export default Stocks
