import React from 'react'

import Breadcrumb, { BreadcrumbStyle } from 'components/Breadcrumb'

import { SIGNUP_JOURNEY_STEP_LIST } from './constants'
import { useActiveStep } from './hooks'

const SignupJourneyBreadcrumb = () => {
  const activeStep = useActiveStep()
  return (
    <Breadcrumb
      activeStep={activeStep}
      steps={SIGNUP_JOURNEY_STEP_LIST}
      styleType={BreadcrumbStyle.STEPPER}
    />
  )
}

export default SignupJourneyBreadcrumb
