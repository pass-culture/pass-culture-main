import React from 'react'

import Breadcrumb, { BreadcrumbStyle, Step } from 'components/Breadcrumb'
import {
  DEFAULT_ACTIVITY_VALUES,
  useSignupJourneyContext,
} from 'context/SignupJourneyContext'
import { DEFAULT_OFFERER_FORM_VALUES } from 'screens/SignupJourneyForm/Offerer/constants'

import { SIGNUP_JOURNEY_STEP_IDS } from './constants'
import { useActiveStep } from './hooks'
import styles from './SignupJourneyBreadcrumb.module.scss'

const SignupJourneyBreadcrumb = () => {
  const { activity, offerer } = useSignupJourneyContext()

  const isActivityStepDisabled =
    activity === null || activity === DEFAULT_ACTIVITY_VALUES

  const isOffererStepDisabled =
    offerer === null || offerer === DEFAULT_OFFERER_FORM_VALUES

  const signupJourneyBreadcrumbSteps: Step[] = [
    {
      id: SIGNUP_JOURNEY_STEP_IDS.AUTHENTICATION,
      label: 'Identification',
      url: '/parcours-inscription/authentification',
    },
    {
      id: SIGNUP_JOURNEY_STEP_IDS.ACTIVITY,
      label: 'Activité',
      url: isActivityStepDisabled
        ? undefined
        : '/parcours-inscription/activite',
    },
    {
      id: SIGNUP_JOURNEY_STEP_IDS.VALIDATION,
      label: 'Validation',
      url:
        isActivityStepDisabled || isOffererStepDisabled
          ? undefined
          : '/parcours-inscription/validation',
    },
  ]

  const activeStep = useActiveStep()
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
