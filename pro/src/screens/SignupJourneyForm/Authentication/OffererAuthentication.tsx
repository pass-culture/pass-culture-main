import { FormikProvider, useFormik } from 'formik'
import React from 'react'
import { useNavigate } from 'react-router-dom-v5-compat'

import FormLayout from 'components/FormLayout'
import { useSignupJourneyContext } from 'context/SignupJourneyContext'
import { FORM_ERROR_MESSAGE } from 'core/shared'
import useNotification from 'hooks/useNotification'

import { ActionBar } from '../ActionBar'
import { DEFAULT_OFFERER_FORM_VALUES } from '../Offerer/constants'

import OffererAuthenticationForm, {
  IOffererAuthenticationFormValues,
} from './OffererAuthenticationForm'
import { validationSchema } from './validationSchema'

const OffererAuthentication = (): JSX.Element => {
  const notify = useNotification()
  const navigate = useNavigate()

  const { offerer, setOfferer } = useSignupJourneyContext()

  const initialValues: IOffererAuthenticationFormValues = offerer
    ? offerer
    : DEFAULT_OFFERER_FORM_VALUES

  const handlePreviousStep = () => {
    navigate('/parcours-inscription/structure')
  }

  const handleNextStep = () => async () => {
    if (Object.keys(formik.errors).length !== 0) {
      notify.error(FORM_ERROR_MESSAGE)
      return
    }
  }

  const onSubmitOffererAuthentication = async (
    formValues: IOffererAuthenticationFormValues
  ): Promise<void> => {
    setOfferer(formValues)
    navigate('/parcours-inscription/activite')
  }

  const formik = useFormik({
    initialValues,
    onSubmit: onSubmitOffererAuthentication,
    validationSchema,
    enableReinitialize: true,
  })

  return (
    <FormLayout>
      <FormikProvider value={formik}>
        <form
          onSubmit={formik.handleSubmit}
          data-testid="signup-offerer-authentication-form"
        >
          <FormLayout.MandatoryInfo />
          <OffererAuthenticationForm />
          <ActionBar
            onClickPrevious={handlePreviousStep}
            previousStepTitle="Retour"
            onClickNext={handleNextStep()}
            isDisabled={formik.isSubmitting}
          />
        </form>
      </FormikProvider>
    </FormLayout>
  )
}

export default OffererAuthentication
