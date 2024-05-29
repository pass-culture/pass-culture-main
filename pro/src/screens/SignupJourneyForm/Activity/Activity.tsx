import { FormikProvider, useFormik } from 'formik'
import React from 'react'
import { useNavigate } from 'react-router-dom'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import { Target } from 'apiClient/v1'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { SIGNUP_JOURNEY_STEP_IDS } from 'components/SignupJourneyStepper/constants'
import { GET_VENUE_TYPES_QUERY_KEY } from 'config/swrQueryKeys'
import {
  useSignupJourneyContext,
  ActivityContext,
} from 'context/SignupJourneyContext/SignupJourneyContext'
import { FORM_ERROR_MESSAGE } from 'core/shared/constants'
import { useNotification } from 'hooks/useNotification'
import { Spinner } from 'ui-kit/Spinner/Spinner'

import { ActionBar } from '../ActionBar/ActionBar'

import { ActivityForm, ActivityFormValues } from './ActivityForm'
import { DEFAULT_ACTIVITY_FORM_VALUES } from './constants'
import { validationSchema } from './validationSchema'

export const Activity = (): JSX.Element => {
  const notify = useNotification()
  const navigate = useNavigate()
  const { activity, setActivity, offerer } = useSignupJourneyContext()

  const venueTypesQuery = useSWR([GET_VENUE_TYPES_QUERY_KEY], () =>
    api.getVenueTypes()
  )
  const venueTypes = venueTypesQuery.data

  const serializeActivityContext = (
    activity: ActivityContext
  ): ActivityFormValues => {
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
    activityForm: ActivityFormValues
  ): ActivityContext => {
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

  const initialValues: ActivityFormValues = activity
    ? serializeActivityContext(activity)
    : DEFAULT_ACTIVITY_FORM_VALUES

  const handleNextStep = () => {
    if (Object.keys(formik.errors).length !== 0) {
      notify.error(FORM_ERROR_MESSAGE)
      return
    }
  }

  const onSubmitActivity = (formValues: ActivityFormValues) => {
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

  if (venueTypesQuery.isLoading) {
    return <Spinner />
  }

  if (!venueTypes) {
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
            onClickNext={handleNextStep}
            isDisabled={formik.isSubmitting}
            previousTo={SIGNUP_JOURNEY_STEP_IDS.AUTHENTICATION}
            nextTo={SIGNUP_JOURNEY_STEP_IDS.VALIDATION}
            legalCategoryCode={offerer?.legalCategoryCode}
          />
        </form>
      </FormikProvider>
    </FormLayout>
  )
}
