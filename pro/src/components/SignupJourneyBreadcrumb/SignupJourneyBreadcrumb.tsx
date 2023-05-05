import React from 'react'
import { useLocation } from 'react-router-dom'

import Breadcrumb, { BreadcrumbStyle, Step } from 'components/Breadcrumb'
import { OnboardingFormNavigationAction } from 'components/SignupJourneyFormLayout/constants'
import {
  DEFAULT_ACTIVITY_VALUES,
  useSignupJourneyContext,
} from 'context/SignupJourneyContext'
import { Events } from 'core/FirebaseEvents/constants'
import useAnalytics from 'hooks/useAnalytics'
import { DEFAULT_OFFERER_FORM_VALUES } from 'screens/SignupJourneyForm/Offerer/constants'

import { SIGNUP_JOURNEY_STEP_IDS } from './constants'
import { useActiveStep } from './hooks'
import styles from './SignupJourneyBreadcrumb.module.scss'

const SignupJourneyBreadcrumb = () => {
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
      logEvent?.(Events.CLICKED_ONBOARDING_FORM_NAVIGATION, {
        from: location.pathname,
        to,
        used: OnboardingFormNavigationAction.Breadcrumb,
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

  const breadcrumbStepIds = signupJourneyBreadcrumbSteps.map(step => step.id)

  if (!breadcrumbStepIds.includes(activeStep)) {
    return <></>
  }

  return (
    <Breadcrumb
      activeStep={activeStep}
      steps={signupJourneyBreadcrumbSteps}
      styleType={BreadcrumbStyle.STEPPER}
      className={styles['signup-breadcrumb']}
    />
  )
}

export default SignupJourneyBreadcrumb
