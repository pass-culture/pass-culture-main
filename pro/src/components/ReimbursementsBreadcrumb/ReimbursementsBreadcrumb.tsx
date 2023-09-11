import React from 'react'

import Breadcrumb, { BreadcrumbStyle } from 'components/Breadcrumb'
import useActiveFeature from 'hooks/useActiveFeature'
import useActiveStep from 'hooks/useActiveStep'

import {
  STEP_LIST,
  STEP_NAMES,
  OLD_STEP_LIST,
  OLD_STEP_NAMES,
} from './constants'

const ReimbursementsBreadcrumb = () => {
  const isNewBankDetailsJourneyEnable = useActiveFeature(
    'WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'
  )
  const activeStep = useActiveStep(
    isNewBankDetailsJourneyEnable ? STEP_NAMES : OLD_STEP_NAMES
  )
  return (
    <Breadcrumb
      activeStep={activeStep}
      steps={isNewBankDetailsJourneyEnable ? STEP_LIST : OLD_STEP_LIST}
      styleType={BreadcrumbStyle.TAB}
    />
  )
}

export default ReimbursementsBreadcrumb
