import { yupResolver } from '@hookform/resolvers/yup'
import { FormProvider, useForm } from 'react-hook-form'
import { useNavigate } from 'react-router'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import { Target } from 'apiClient/v1'
import { MainHeading } from 'app/App/layout/Layout'
import { GET_VENUE_TYPES_QUERY_KEY } from 'commons/config/swrQueryKeys'
import {
  ActivityContext,
  useSignupJourneyContext,
} from 'commons/context/SignupJourneyContext/SignupJourneyContext'
import { FORM_ERROR_MESSAGE } from 'commons/core/shared/constants'
import { useNotification } from 'commons/hooks/useNotification'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { SIGNUP_JOURNEY_STEP_IDS } from 'components/SignupJourneyStepper/constants'
import { Spinner } from 'ui-kit/Spinner/Spinner'

import { ActionBar } from '../ActionBar/ActionBar'

import styles from './Activity.module.scss'
import { ActivityForm, ActivityFormValues } from './ActivityForm'
import { defaultActivityFormValues } from './constants'
import { validationSchema } from './validationSchema'

export const Activity = (): JSX.Element => {
  const notify = useNotification()
  const navigate = useNavigate()
  const { activity, setActivity } = useSignupJourneyContext()

  const { data: venueTypes, isLoading } = useSWR(
    [GET_VENUE_TYPES_QUERY_KEY],
    () => api.getVenueTypes()
  )

  const serializeActivityContext = (
    activity: ActivityContext
  ): ActivityFormValues => {
    return {
      ...activity,
      socialUrls:
        activity.socialUrls.length === 0
          ? [{ url: '' }]
          : activity.socialUrls.map((urlString) => ({ url: urlString })),
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

  const methods = useForm({
    defaultValues: activity
      ? serializeActivityContext(activity)
      : defaultActivityFormValues,
    resolver: yupResolver(validationSchema),
  })

  const serializeActivityFormToSubmit = (
    activityForm: ActivityFormValues
  ): ActivityContext => {
    const { individual, educational } = activityForm.targetCustomer
    return {
      ...activityForm,
      socialUrls: activityForm.socialUrls
        .filter(({ url }) => url.trim() !== '') // garder que ceux où url n'est pas vide
        .map(({ url }) => url),
      targetCustomer: individual
        ? educational
          ? Target.INDIVIDUAL_AND_EDUCATIONAL
          : Target.INDIVIDUAL
        : Target.EDUCATIONAL,
    }
  }

  const handleNextStep = () => {
    if (!methods.formState.isValid) {
      notify.error(FORM_ERROR_MESSAGE)
      return
    }
  }

  const onSubmit = (formValues: any) => {
    setActivity(serializeActivityFormToSubmit(formValues))
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    navigate('/parcours-inscription/validation')
  }

  const handlePreviousStep = () => {
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    navigate('/parcours-inscription/identification')
  }

  if (isLoading) {
    return <Spinner />
  }

  if (!venueTypes) {
    return <></>
  }

  return (
    <FormLayout>
      <FormProvider {...methods}>
        <form
          onSubmit={methods.handleSubmit(onSubmit)}
          data-testid="signup-activity-form"
        >
          {/* eslint-disable-next-line react/forbid-elements */}
          <MainHeading
            mainHeading="Votre structure"
            className={styles['main-heading-wrapper']}
          />
          <h2 className={styles['subtitle']}>
            Et enfin, définissez l’activité de votre structure
          </h2>
          <FormLayout.MandatoryInfo />
          <ActivityForm venueTypes={venueTypes} />
          <ActionBar
            onClickPrevious={handlePreviousStep}
            onClickNext={handleNextStep}
            isDisabled={methods.formState.isSubmitting}
            previousTo={SIGNUP_JOURNEY_STEP_IDS.AUTHENTICATION}
            nextTo={SIGNUP_JOURNEY_STEP_IDS.VALIDATION}
          />
        </form>
      </FormProvider>
    </FormLayout>
  )
}
