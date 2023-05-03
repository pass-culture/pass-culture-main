import { FormikProvider, useFormik } from 'formik'
import React from 'react'
import { useNavigate } from 'react-router-dom'

import { Target } from 'apiClient/v1'
import FormLayout from 'components/FormLayout'
import { SIGNUP_JOURNEY_STEP_IDS } from 'components/SignupJourneyBreadcrumb/constants'
import { useSignupJourneyContext } from 'context/SignupJourneyContext'
import { IActivity } from 'context/SignupJourneyContext/SignupJourneyContext'
import { FORM_ERROR_MESSAGE } from 'core/shared'
import { useGetVenueTypes } from 'core/Venue/adapters/getVenueTypeAdapter'
import useAnalytics from 'hooks/useAnalytics'
import useNotification from 'hooks/useNotification'
import Spinner from 'ui-kit/Spinner/Spinner'

import { ActionBar } from '../ActionBar'

import ActivityForm, { IActivityFormValues } from './ActivityForm'
import { DEFAULT_ACTIVITY_FORM_VALUES } from './constants'
import { validationSchema } from './validationSchema'

const Activity = (): JSX.Element => {
  const {
    isLoading: isLoadingVenueTypes,
    error: errorVenueTypes,
    data: venueTypes,
  } = useGetVenueTypes()
  const notify = useNotification()
  const navigate = useNavigate()
  const { activity, setActivity } = useSignupJourneyContext()
  const { logEvent } = useAnalytics()

  const serializeActivityContext = (
    activity: IActivity
  ): IActivityFormValues => {
    return {
      ...activity,
      targetCustomer: {
        individual: Boolean(
          activity.targetCustomer === Target.INDIVIDUAL_AND_EDUCATIONAL ||
            activity.targetCustomer === Target.INDIVIDUAL
        ),
        educational: Boolean(
          activity.targetCustomer === Target.INDIVIDUAL_AND_EDUCATIONAL ||
            activity.targetCustomer === Target.EDUCATIONAL
        ),
      },
    }
  }

  const serializeActivityFormToSubmit = (
    activityForm: IActivityFormValues
  ): IActivity => {
    const { individual, educational } = activityForm.targetCustomer
    let serializedTargetCustomer

    if (individual && educational) {
      serializedTargetCustomer = Target.INDIVIDUAL_AND_EDUCATIONAL
    } else if (individual) {
      serializedTargetCustomer = Target.INDIVIDUAL
    } else {
      serializedTargetCustomer = Target.EDUCATIONAL
    }

    return {
      ...activityForm,
      targetCustomer: serializedTargetCustomer,
    }
  }

  const initialValues: IActivityFormValues = activity
    ? serializeActivityContext(activity)
    : DEFAULT_ACTIVITY_FORM_VALUES

  const handleNextStep = () => async () => {
    if (Object.keys(formik.errors).length !== 0) {
      notify.error(FORM_ERROR_MESSAGE)
      return
    }
  }

  const onSubmitActivity = async (
    formValues: IActivityFormValues
  ): Promise<void> => {
    setActivity(serializeActivityFormToSubmit(formValues))
    navigate('/parcours-inscription/validation')
  }

  const formik = useFormik({
    initialValues,
    onSubmit: onSubmitActivity,
    validationSchema,
    enableReinitialize: true,
  })

  const handlePreviousStep = () => {
    navigate('/parcours-inscription/identification')
  }

  if (isLoadingVenueTypes) {
    return <Spinner />
  }

  if (errorVenueTypes) {
    return <></>
  }

  return (
    <FormLayout>
      <FormikProvider value={formik}>
        <form onSubmit={formik.handleSubmit} data-testid="signup-activity-form">
          <FormLayout.MandatoryInfo />
          <ActivityForm venueTypes={venueTypes} />
          <ActionBar
            onClickPrevious={handlePreviousStep}
            onClickNext={handleNextStep()}
            isDisabled={formik.isSubmitting}
            previousTo={SIGNUP_JOURNEY_STEP_IDS.AUTHENTICATION}
            nextTo={SIGNUP_JOURNEY_STEP_IDS.VALIDATION}
            logEvent={logEvent}
          />
        </form>
      </FormikProvider>
    </FormLayout>
  )
}

export default Activity
