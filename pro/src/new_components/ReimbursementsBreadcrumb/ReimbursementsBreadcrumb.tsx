import React from 'react'

import Breadcrumb, { BreadcrumbStyle } from 'new_components/Breadcrumb'

import { STEP_LIST } from './constants'
import useActiveStep from './hooks/useActiveStep'

const ReimbursementsBreadcrumb = () => {
  const activeStep = useActiveStep()
  return (
    <Breadcrumb
      activeStep={activeStep}
      steps={STEP_LIST}
      styleType={BreadcrumbStyle.TAB}
    />
  )
}

export default ReimbursementsBreadcrumb
