import React from 'react'

import Breadcrumb, { BreadcrumbStyle } from 'components/Breadcrumb'
import { useReimbursementContext } from 'context/ReimbursementContext/ReimbursementContext'
import useActiveFeature from 'hooks/useActiveFeature'
import useActiveStep from 'hooks/useActiveStep'

import {
  OLD_STEP_LIST,
  OLD_STEP_NAMES,
  STEP_ID_BANK_INFORMATIONS,
  STEP_LIST,
  STEP_NAMES,
} from './constants'

const ReimbursementsBreadcrumb = () => {
  const isNewBankDetailsJourneyEnable = useActiveFeature(
    'WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'
  )
  const { selectedOfferer } = useReimbursementContext()

  const activeStep = useActiveStep(
    isNewBankDetailsJourneyEnable ? STEP_NAMES : OLD_STEP_NAMES
  )

  const getSteps = () => {
    return STEP_LIST.map(step => {
      if (step.id === STEP_ID_BANK_INFORMATIONS) {
        step.hasWarning =
          (selectedOfferer &&
            selectedOfferer?.venuesWithNonFreeOffersWithoutBankAccounts.length >
              0) ??
          false
      }
      return step
    })
  }

  return (
    <Breadcrumb
      activeStep={activeStep}
      steps={isNewBankDetailsJourneyEnable ? getSteps() : OLD_STEP_LIST}
      styleType={BreadcrumbStyle.TAB}
    />
  )
}

export default ReimbursementsBreadcrumb
