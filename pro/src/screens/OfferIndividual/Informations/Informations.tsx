import { useFormik, FormikProvider } from 'formik'
import React from 'react'
import { useHistory } from 'react-router-dom'

import Breadcrumb, { BreadcrumbStyle } from 'new_components/Breadcrumb'
import { OfferFormLayout } from 'new_components/OfferFormLayout'
import { OfferIndividualForm } from 'new_components/OfferIndividualForm'
import {
  CREATION_STEP_PATTERNS,
  OFFER_FORM_STEP_IDS,
} from 'screens/OfferIndividual/constants'

import { ActionBar } from '../ActionBar'
import { buildStepList } from '../utils'

const Informations = (): JSX.Element => {
  const history = useHistory()

  const stepList = buildStepList({ stepPatternList: CREATION_STEP_PATTERNS })
  const handleNextStep = () => {
    // TODO get a real id after offer creation form submit
    const testCreatedOfferId = 'AL4Q'
    history.push(`/offre/${testCreatedOfferId}/v3/creation/individuelle/stocks`)
  }
  const initialValues = {}
  const onSubmit = () => {
    // TODO submit function
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
          activeStep={OFFER_FORM_STEP_IDS.INFORMATIONS}
          steps={Object.values(stepList)}
          styleType={BreadcrumbStyle.TAB}
        />
      </OfferFormLayout.Stepper>

      <OfferFormLayout.Content>
        <FormikProvider value={{ ...formik, resetForm }}>
          <form onSubmit={formik.handleSubmit}>
            <OfferIndividualForm />

            <OfferFormLayout.ActionBar>
              <ActionBar onClickNext={handleNextStep} />
            </OfferFormLayout.ActionBar>
          </form>
        </FormikProvider>
      </OfferFormLayout.Content>
    </OfferFormLayout>
  )
}

export default Informations
