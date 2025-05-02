import { FormikProvider, useFormik } from 'formik'
import { useNavigate } from 'react-router'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import { Target } from 'apiClient/v1'
import { GET_VENUE_TYPES_QUERY_KEY } from 'commons/config/swrQueryKeys'
import {
  useSignupJourneyContext,
  ActivityContext,
} from 'commons/context/SignupJourneyContext/SignupJourneyContext'
import { FORM_ERROR_MESSAGE } from 'commons/core/shared/constants'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { useNotification } from 'commons/hooks/useNotification'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { SIGNUP_JOURNEY_STEP_IDS } from 'components/SignupJourneyStepper/constants'
import { Spinner } from 'ui-kit/Spinner/Spinner'

import { ActionBar } from '../ActionBar/ActionBar'

import { ActivityForm, ActivityFormValues } from './ActivityForm'
import { defaultActivityFormValues } from './constants'
import { validationSchema } from './validationSchema'

export const Activity = (): JSX.Element => {
  const notify = useNotification()
  const navigate = useNavigate()
  const isNewSignupEnabled = useActiveFeature('WIP_2025_SIGN_UP')
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
    : defaultActivityFormValues(isNewSignupEnabled)

  const handleNextStep = () => {
    if (Object.keys(formik.errors).length !== 0) {
      notify.error(FORM_ERROR_MESSAGE)
      return
    }
  }

  const onSubmitActivity = (formValues: ActivityFormValues) => {
    setActivity(serializeActivityFormToSubmit(formValues))
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    navigate('/parcours-inscription/validation')
  }

  const formik = useFormik({
    initialValues,
    onSubmit: onSubmitActivity,
    validationSchema: validationSchema(isNewSignupEnabled),
    enableReinitialize: true,
  })

  const handlePreviousStep = () => {
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
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
