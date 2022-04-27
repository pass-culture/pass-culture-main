import { useFormik, FormikProvider } from 'formik'
import React from 'react'
import { useHistory } from 'react-router-dom'

import Breadcrumb, { BreadcrumbStyle } from 'new_components/Breadcrumb'
import { OfferFormLayout } from 'new_components/OfferFormLayout'
import {
  OfferIndividualForm,
  IOfferIndividualFormValues,
  validationSchema,
} from 'new_components/OfferIndividualForm'
import { OFFER_FORM_STEP_IDS } from 'screens/OfferIndividual/constants'

import { ActionBar } from '../ActionBar'
import { fakeOffer } from '../constants'
import { getStepsOffer } from '../utils/steps'

interface IInformationsProps {
  initialValues: IOfferIndividualFormValues
}

const Informations = ({ initialValues }: IInformationsProps): JSX.Element => {
  const history = useHistory()

  // call getStep with offer when this screen get it as prop
  const { stepList, activeSteps } = getStepsOffer(fakeOffer)
  const handleNextStep = () => {
    // TODO get a real id after offer creation form submit
    history.push(`/offre/${fakeOffer.id}/v3/creation/individuelle/stocks`)
  }

  const onSubmit = () => {
    // TODO submit function
  }

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
              <ActionBar
                disableNext={!activeSteps.includes(OFFER_FORM_STEP_IDS.STOCKS)}
                onClickNext={handleNextStep}
              />
            </OfferFormLayout.ActionBar>
          </form>
        </FormikProvider>
      </OfferFormLayout.Content>
    </OfferFormLayout>
  )
}

export default Informations
