import React from 'react'

import Breadcrumb, { BreadcrumbStyle } from 'components/Breadcrumb'

import { STEP_LIST } from './constants'
import { useActiveStep } from './hooks'

const SignupBreadcrumb = () => {
  const activeStep = useActiveStep()
  return (
    <Breadcrumb
      activeStep={activeStep}
      steps={STEP_LIST}
      styleType={BreadcrumbStyle.STEPPER}
    />
  )
}

export default SignupBreadcrumb
