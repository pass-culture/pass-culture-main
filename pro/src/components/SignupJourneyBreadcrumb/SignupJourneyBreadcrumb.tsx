import React from 'react'

import Breadcrumb, { BreadcrumbStyle } from 'components/Breadcrumb'

import { SIGNUP_JOURNEY_BREADCRUMB_STEPS } from './constants'
import { useActiveStep } from './hooks'

const SignupJourneyBreadcrumb = () => {
  const activeStep = useActiveStep()
  const breadcrumbStepIds = SIGNUP_JOURNEY_BREADCRUMB_STEPS.map(step => step.id)

  if (!breadcrumbStepIds.includes(activeStep)) {
    return <></>
  }

  return (
    <Breadcrumb
      activeStep={activeStep}
      steps={SIGNUP_JOURNEY_BREADCRUMB_STEPS}
      styleType={BreadcrumbStyle.STEPPER}
    />
  )
}

export default SignupJourneyBreadcrumb
