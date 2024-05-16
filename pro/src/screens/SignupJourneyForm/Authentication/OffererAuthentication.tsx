import { FormikProvider, useFormik } from 'formik'
import React, { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

import useAnalytics from 'app/App/analytics/firebase'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { SIGNUP_JOURNEY_STEP_IDS } from 'components/SignupJourneyStepper/constants'
import { useSignupJourneyContext } from 'context/SignupJourneyContext'

import { ActionBar } from '../ActionBar'
import { DEFAULT_OFFERER_FORM_VALUES } from '../Offerer/constants'

import styles from './OffererAuthentication.module.scss'
import OffererAuthenticationForm, {
  OffererAuthenticationFormValues,
} from './OffererAuthenticationForm'
import { validationSchema } from './validationSchema'

export const OffererAuthentication = (): JSX.Element => {
  const { logEvent } = useAnalytics()
  const navigate = useNavigate()

  const { offerer, setOfferer } = useSignupJourneyContext()

  const initialValues: OffererAuthenticationFormValues = {
    ...DEFAULT_OFFERER_FORM_VALUES,
    ...offerer,
    addressAutocomplete: `${offerer?.street} ${offerer?.postalCode} ${offerer?.city}`,
    'search-addressAutocomplete': `${offerer?.street} ${offerer?.postalCode} ${offerer?.city}`,
  }

  const handlePreviousStep = () => {
    setOfferer(null)
    navigate('/parcours-inscription/structure')
  }

  const onSubmitOffererAuthentication = (
    formValues: OffererAuthenticationFormValues
  ) => {
    setOfferer({
      ...formValues,
      hasVenueWithSiret: false,
      legalCategoryCode: offerer?.legalCategoryCode,
    })
    navigate('/parcours-inscription/activite')
  }

  const formik = useFormik({
    initialValues,
    onSubmit: onSubmitOffererAuthentication,
    validationSchema,
    enableReinitialize: true,
  })

  useEffect(() => {
    if (offerer?.siret === '' || offerer?.name === '') {
      handlePreviousStep()
    }
  }, [])

  return (
    <FormLayout>
      <FormikProvider value={formik}>
        <form
          className={styles['signup-offerer-authentication-form']}
          onSubmit={formik.handleSubmit}
          data-testid="signup-offerer-authentication-form"
        >
          <FormLayout.MandatoryInfo />
          <OffererAuthenticationForm />
          <ActionBar
            onClickPrevious={handlePreviousStep}
            previousTo={SIGNUP_JOURNEY_STEP_IDS.OFFERER}
            nextTo={SIGNUP_JOURNEY_STEP_IDS.ACTIVITY}
            previousStepTitle="Retour"
            isDisabled={formik.isSubmitting}
            logEvent={logEvent}
            legalCategoryCode={offerer?.legalCategoryCode}
          />
        </form>
      </FormikProvider>
    </FormLayout>
  )
}
