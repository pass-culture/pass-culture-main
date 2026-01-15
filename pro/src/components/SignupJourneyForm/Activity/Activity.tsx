import { yupResolver } from '@hookform/resolvers/yup'
import { FormProvider, useForm } from 'react-hook-form'
import { useNavigate } from 'react-router'
import useSWR from 'swr'

import { api } from '@/apiClient/api'
import { Target } from '@/apiClient/v1'
import { GET_VENUE_TYPES_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import {
  type ActivityContext,
  useSignupJourneyContext,
} from '@/commons/context/SignupJourneyContext/SignupJourneyContext'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { SIGNUP_JOURNEY_STEP_IDS } from '@/components/SignupJourneyStepper/constants'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import { ActionBar } from '../ActionBar/ActionBar'
import styles from './Activity.module.scss'
import { ActivityForm, type ActivityFormValues } from './ActivityForm'
import { defaultActivityFormValues } from './constants'
import { validationSchema } from './validationSchema'

export const Activity = (): JSX.Element => {
  const navigate = useNavigate()
  const { activity, setActivity, offerer } = useSignupJourneyContext()
  const isCulturalDomainsEnabled = useActiveFeature(
    'WIP_VENUE_CULTURAL_DOMAINS'
  )

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
    resolver: yupResolver(
      validationSchema(
        isCulturalDomainsEnabled,
        offerer?.isOpenToPublic === 'false'
      )
    ),
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

  const onSubmit = (formValues: any) => {
    setActivity(serializeActivityFormToSubmit(formValues))
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    navigate('/inscription/structure/confirmation')
  }

  const handlePreviousStep = () => {
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    navigate('/inscription/structure/identification')
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
          <h2 className={styles['subtitle']}>
            Et enfin, définissez l’activité de votre structure
          </h2>
          <FormLayout.MandatoryInfo />
          <ActivityForm venueTypes={venueTypes} />
          <ActionBar
            onClickPrevious={handlePreviousStep}
            isDisabled={methods.formState.isSubmitting}
            previousTo={SIGNUP_JOURNEY_STEP_IDS.AUTHENTICATION}
            nextTo={SIGNUP_JOURNEY_STEP_IDS.CONFIRMATION}
          />
        </form>
      </FormProvider>
    </FormLayout>
  )
}
