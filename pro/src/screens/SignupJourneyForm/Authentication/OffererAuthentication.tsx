import { FormikProvider, useFormik } from 'formik'
import React, { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

import FormLayout from 'components/FormLayout'
import { SIGNUP_JOURNEY_STEP_IDS } from 'components/SignupJourneyBreadcrumb/constants'
import { useSignupJourneyContext } from 'context/SignupJourneyContext'
import useAnalytics from 'hooks/useAnalytics'

import { ActionBar } from '../ActionBar'
import { DEFAULT_OFFERER_FORM_VALUES } from '../Offerer/constants'

import styles from './OffererAuthentication.module.scss'
import OffererAuthenticationForm, {
  IOffererAuthenticationFormValues,
} from './OffererAuthenticationForm'
import { validationSchema } from './validationSchema'

const OffererAuthentication = (): JSX.Element => {
  const { logEvent } = useAnalytics()
  const navigate = useNavigate()

  const { offerer, setOfferer } = useSignupJourneyContext()

  const initialValues: IOffererAuthenticationFormValues = {
    ...DEFAULT_OFFERER_FORM_VALUES,
    ...offerer,
    addressAutocomplete: `${offerer?.address} ${offerer?.postalCode} ${offerer?.city}`,
    'search-addressAutocomplete': `${offerer?.address} ${offerer?.postalCode} ${offerer?.city}`,
  }

  const handlePreviousStep = () => {
    setOfferer(null)
    navigate('/parcours-inscription/structure')
  }

  const onSubmitOffererAuthentication = async (
    formValues: IOffererAuthenticationFormValues
  ): Promise<void> => {
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

export default OffererAuthentication
