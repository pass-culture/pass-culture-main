import { yupResolver } from '@hookform/resolvers/yup'
import { FormProvider, useForm } from 'react-hook-form'
import { useNavigate } from 'react-router'

import { Target } from '@/apiClient/v1'
import {
  type ActivityContext,
  cleanSignupJourneyStorage,
  RESTORE_ERRORS,
  saveActivityToStorage,
  tryRestoreActivityFromStorage,
  tryRestoreInitialAddressFromStorage,
  tryRestoreOffererFromStorage,
  useSignupJourneyContext,
} from '@/commons/context/SignupJourneyContext/SignupJourneyContext'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { SIGNUP_JOURNEY_STEP_IDS } from '@/components/SignupJourneyStepper/constants'

import { ActionBar } from '../ActionBar/ActionBar'
import styles from './Activity.module.scss'
import { ActivityForm, type ActivityFormValues } from './ActivityForm'
import { defaultActivityFormValues } from './constants'
import { validationSchema } from './validationSchema'
import { useCallback, useEffect } from 'react'
import {
  DEFAULT_ADDRESS_FORM_VALUES,
  DEFAULT_OFFERER_FORM_VALUES,
} from '../Offerer/constants'
import { DEFAULT_ACTIVITY_VALUES } from '@/commons/context/SignupJourneyContext/constants'

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

export const Activity = () => {
  const navigate = useNavigate()
  const {
    activity,
    setActivity,
    offerer,
    setOfferer,
    initialAddress,
    setInitialAddress,
  } = useSignupJourneyContext()

  const methods = useForm<ActivityFormValues>({
    defaultValues: activity
      ? serializeActivityContext(activity)
      : defaultActivityFormValues,
    resolver: yupResolver(
      validationSchema(offerer?.isOpenToPublic === 'false')
    ),
  })

  const onSubmit = (formValues: ActivityFormValues) => {
    const activityFormValues = serializeActivityFormToSubmit(formValues)
    saveActivityToStorage(activityFormValues)
    setActivity(activityFormValues)

    navigate('/inscription/structure/confirmation')
  }

  const handlePreviousStep = useCallback(() => {
    navigate('/inscription/structure/identification')
  }, [navigate])

  useEffect(() => {
    // Try to restore the "offerer" and "initialAddress" context from storage
    if (
      offerer === null ||
      offerer === DEFAULT_OFFERER_FORM_VALUES ||
      initialAddress === null ||
      initialAddress === DEFAULT_ADDRESS_FORM_VALUES
    ) {
      try {
        tryRestoreOffererFromStorage(setOfferer)
        tryRestoreInitialAddressFromStorage(setInitialAddress)
      } catch {
        cleanSignupJourneyStorage()
        navigate('/inscription/structure/recherche')
        return
      }
    }

    // We must try to restore the "activity" context separately from above
    // because the error handling in the catch block isn't the same
    if (activity === null || activity === DEFAULT_ACTIVITY_VALUES) {
      try {
        const storedActivity = tryRestoreActivityFromStorage(setActivity)
        methods.reset(serializeActivityContext(storedActivity))
      } catch (error: unknown) {
        if (
          (error as Error).message ===
          RESTORE_ERRORS.NO_ACTIVITY_DATA_IN_STORAGE
        ) {
          // It's okay here if there is no activity data in storage, as we are on activity page
          return
        }
        // If this is another error, we redirect to the search page
        cleanSignupJourneyStorage()
        navigate('/inscription/structure/recherche')
        return
      }
    }
  }, [
    offerer,
    activity,
    setOfferer,
    setActivity,
    initialAddress,
    setInitialAddress,
    methods,
    navigate,
  ])

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
          <ActivityForm />
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
