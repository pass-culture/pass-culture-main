import React from 'react'
import { useLocation } from 'react-router-dom'

import { useAnalytics } from 'app/App/analytics/firebase'
import { OnboardingFormNavigationAction } from 'components/SignupJourneyFormLayout/constants'
import { Step, Stepper } from 'components/Stepper/Stepper'
import { DEFAULT_ACTIVITY_VALUES } from 'context/SignupJourneyContext/constants'
import { useSignupJourneyContext } from 'context/SignupJourneyContext/SignupJourneyContext'
import { Events } from 'core/FirebaseEvents/constants'
import { useActiveStep } from 'hooks/useActiveStep'
import { DEFAULT_OFFERER_FORM_VALUES } from 'screens/SignupJourneyForm/Offerer/constants'

import { SIGNUP_JOURNEY_STEP_IDS } from './constants'
import styles from './SignupJourneyStepper.module.scss'

export const SignupJourneyStepper = () => {
  const { activity, offerer } = useSignupJourneyContext()

  const { logEvent } = useAnalytics()

  const isActivityStepDisabled =
    activity === null || activity === DEFAULT_ACTIVITY_VALUES

  const isOffererStepDisabled =
    offerer === null || offerer === DEFAULT_OFFERER_FORM_VALUES

  const everyStepActivated = !isActivityStepDisabled && !isOffererStepDisabled

  const location = useLocation()
  const activeStep = useActiveStep()

  const logBreadcrumbClick = (to: SIGNUP_JOURNEY_STEP_IDS, stepUrl: string) => {
    if (stepUrl.indexOf(activeStep) === -1) {
      logEvent(Events.CLICKED_ONBOARDING_FORM_NAVIGATION, {
        from: location.pathname,
        to,
        used: OnboardingFormNavigationAction.Breadcrumb,
        categorieJuridiqueUniteLegale: offerer?.legalCategoryCode,
      })
    }
  }

  const signupJourneyBreadcrumbSteps: Step[] = [
    {
      id: SIGNUP_JOURNEY_STEP_IDS.AUTHENTICATION,
      label: 'Identification',
      url: '/parcours-inscription/identification',
      onClick: () =>
        logBreadcrumbClick(
          SIGNUP_JOURNEY_STEP_IDS.AUTHENTICATION,
          '/parcours-inscription/identification'
        ),
    },
    {
      id: SIGNUP_JOURNEY_STEP_IDS.ACTIVITY,
      label: 'Activité',
      url: isActivityStepDisabled
        ? undefined
        : '/parcours-inscription/activite',
      onClick: () => {
        if (!isActivityStepDisabled) {
          logBreadcrumbClick(
            SIGNUP_JOURNEY_STEP_IDS.ACTIVITY,
            '/parcours-inscription/activite'
          )
        }
      },
    },
    {
      id: SIGNUP_JOURNEY_STEP_IDS.VALIDATION,
      label: 'Validation',
      url: !everyStepActivated ? undefined : '/parcours-inscription/validation',
      onClick: () => {
        if (everyStepActivated) {
          logBreadcrumbClick(
            SIGNUP_JOURNEY_STEP_IDS.VALIDATION,
            '/parcours-inscription/validation'
          )
        }
      },
    },
  ]

  const stepsIds = signupJourneyBreadcrumbSteps.map((step) => step.id)

  if (!stepsIds.includes(activeStep)) {
    return <></>
  }

  return (
    <Stepper
      activeStep={activeStep}
      steps={signupJourneyBreadcrumbSteps}
      className={styles['signup-stepper']}
    />
  )
}
