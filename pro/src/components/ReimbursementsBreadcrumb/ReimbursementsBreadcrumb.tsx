import React from 'react'

import Breadcrumb, { BreadcrumbStyle } from 'components/Breadcrumb'
import useActiveStep from 'hooks/useActiveStep'

import { STEP_LIST, STEP_NAMES } from './constants'

const ReimbursementsBreadcrumb = () => {
  const activeStep = useActiveStep(STEP_NAMES)
  return (
    <Breadcrumb
      activeStep={activeStep}
      steps={STEP_LIST}
      styleType={BreadcrumbStyle.TAB}
    />
  )
}

export default ReimbursementsBreadcrumb
