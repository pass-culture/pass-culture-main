import Breadcrumb, { BreadcrumbStyle } from 'new_components/Breadcrumb'
import { FormikProvider, useFormik } from 'formik'
import {
  IOfferIndividualFormValues,
  OfferIndividualForm,
  validationSchema,
} from 'new_components/OfferIndividualForm'

import { ActionBar } from '../ActionBar'
import { OFFER_FORM_STEP_IDS } from 'screens/OfferIndividual/constants'
import { OfferFormLayout } from 'new_components/OfferFormLayout'
import React from 'react'
import Spinner from 'components/layout/Spinner'
import { TOfferIndividualVenue } from 'core/Venue/types'
import { TOffererName } from 'core/Offerers/types'
import { fakeOffer } from '../constants'
import { getStepsOffer } from '../utils/steps'
import { useHistory } from 'react-router-dom'

export interface IInformationsProps {
  createOfferAdapter: (
    formValues: IOfferIndividualFormValues
  ) => Promise<string | void>
  initialValues: IOfferIndividualFormValues
  isParentReady: boolean
  offererNames: TOffererName[]
  venueList: TOfferIndividualVenue[]
}

const Informations = ({
  createOfferAdapter,
  initialValues,
  isParentReady,
  offererNames,
  venueList,
}: IInformationsProps): JSX.Element => {
  const history = useHistory()

  // call getStep with offer when this screen get it as prop
  const { stepList, activeSteps } = getStepsOffer(fakeOffer)
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
            {isParentReady ? (
              <OfferIndividualForm
                offererNames={offererNames}
                venueList={venueList}
              />
            ) : (
              <Spinner />
            )}
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
