import { yupResolver } from '@hookform/resolvers/yup'
import cn from 'classnames'
import { useCallback, useEffect } from 'react'
import { FormProvider, useForm } from 'react-hook-form'
import { useNavigate } from 'react-router'

import { Target } from '@/apiClient/v1/new'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { MainHeading } from '@/app/App/layouts/components/MainHeading/MainHeading'
import { DEFAULT_ACTIVITY_VALUES } from '@/commons/context/SignupJourneyContext/constants'
import {
  type ActivityContext,
  useSignupJourneyContext,
} from '@/commons/context/SignupJourneyContext/SignupJourneyContext'
import {
  cleanSignupJourneyStorage,
  RESTORE_ERRORS,
  saveActivityToStorage,
  tryRestoreActivityFromStorage,
  tryRestoreInitialAddressFromStorage,
  tryRestoreOffererFromStorage,
} from '@/commons/context/SignupJourneyContext/storage'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { SIGNUP_JOURNEY_STEP_IDS } from '@/components/SignupJourneyStepper/constants'
import { SIGNUP_STEP_IDS } from '@/components/SignupStepper/constants'
import { SignupStepper } from '@/components/SignupStepper/SignupStepper'
import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'

import { ActionBar } from '../ActionBar/ActionBar'
import {
  DEFAULT_ADDRESS_FORM_VALUES,
  DEFAULT_OFFERER_FORM_VALUES,
} from '../Offerer/constants'
import styles from './Activity.module.scss'
import { ActivityForm, type ActivityFormValues } from './ActivityForm'
import { defaultActivityFormValues } from './constants'
import { validationSchema } from './validationSchema'

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

  const isSignupSimulationEnabled = useActiveFeature(
    'WIP_PRE_SIGNUP_SIMULATION'
  )

  const { logEvent } = useAnalytics()

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
    <div
      className={cn({
        [styles['activity-container']]: isSignupSimulationEnabled,
      })}
    >
      {isSignupSimulationEnabled && (
        <>
          <SignupStepper />
          <MainHeading
            mainHeading="Votre activité"
            className={styles['main-heading']}
          />
          <p className={styles['subheading-description']}>
            Ces informations déterminent la visibilité de vos offres auprès des
            jeunes et des enseignants. Les champs suivis d’un * sont
            obligatoires.
          </p>
        </>
      )}

      <FormLayout>
        <FormProvider {...methods}>
          <form
            onSubmit={methods.handleSubmit(onSubmit)}
            data-testid="signup-activity-form"
          >
            {!isSignupSimulationEnabled && (
              <>
                <h2 className={styles['subtitle']}>
                  Et enfin, définissez l’activité de votre structure
                </h2>
                <FormLayout.MandatoryInfo />
              </>
            )}
            <ActivityForm />

            {isSignupSimulationEnabled ? (
              <div className={styles['next-actions']}>
                <Button
                  type="button"
                  label="Retour"
                  variant={ButtonVariant.SECONDARY}
                  onClick={() => {
                    logEvent(Events.CLICKED_ONBOARDING_FORM_NAVIGATION, {
                      from: location.pathname,
                      to: SIGNUP_STEP_IDS.STRUCTURE_IDENTIFICATION,
                      used: 'Retour',
                    })
                    handlePreviousStep()
                  }}
                  disabled={methods.formState.isSubmitting}
                />
                <Button
                  type="submit"
                  label="Continuer"
                  onClick={() => {
                    logEvent(Events.CLICKED_ONBOARDING_FORM_NAVIGATION, {
                      from: location.pathname,
                      to: SIGNUP_STEP_IDS.VALIDATION,
                      used: 'Continuer',
                    })
                  }}
                  disabled={methods.formState.isSubmitting}
                />
              </div>
            ) : (
              <ActionBar
                onClickPrevious={handlePreviousStep}
                isDisabled={methods.formState.isSubmitting}
                previousTo={SIGNUP_JOURNEY_STEP_IDS.AUTHENTICATION}
                nextTo={SIGNUP_JOURNEY_STEP_IDS.CONFIRMATION}
                nextStepTitle="Continuer"
                previousStepTitle="Retour"
              />
            )}
          </form>
        </FormProvider>
      </FormLayout>
    </div>
  )
}
