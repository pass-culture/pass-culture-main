import React from 'react'

import Breadcrumb, { BreadcrumbStyle, Step } from 'components/Breadcrumb'
import { useSignupJourneyContext } from 'context/SignupJourneyContext'
import { DEFAULT_ACTIVITY_FORM_VALUES } from 'screens/SignupJourneyForm/Activity/constants'
import { DEFAULT_OFFERER_FORM_VALUES } from 'screens/SignupJourneyForm/Offerer/constants'

import { SIGNUP_JOURNEY_STEP_IDS } from './constants'
import { useActiveStep } from './hooks'

const SignupJourneyBreadcrumb = () => {
  const { activity, offerer } = useSignupJourneyContext()

  const isActivityStepDisable =
    activity === null || activity == DEFAULT_ACTIVITY_FORM_VALUES

  const isOffererStepDisable =
    offerer === null || offerer == DEFAULT_OFFERER_FORM_VALUES

  const signupJourneyBreadcrumbSteps: Step[] = [
    {
      id: SIGNUP_JOURNEY_STEP_IDS.AUTHENTICATION,
      label: 'Authentification',
      url: '/parcours-inscription/authentification',
    },
    {
      id: SIGNUP_JOURNEY_STEP_IDS.ACTIVITY,
      label: 'Activité',
      url: isActivityStepDisable ? undefined : '/parcours-inscription/activite',
    },
    {
      id: SIGNUP_JOURNEY_STEP_IDS.VALIDATION,
      label: 'Validation',
      url:
        isActivityStepDisable || isOffererStepDisable
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
    />
  )
}

export default SignupJourneyBreadcrumb
