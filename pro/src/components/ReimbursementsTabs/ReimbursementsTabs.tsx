import React from 'react'

import { useReimbursementContext } from 'context/ReimbursementContext/ReimbursementContext'
import useActiveFeature from 'hooks/useActiveFeature'
import useActiveStep from 'hooks/useActiveStep'
import fullErrorIcon from 'icons/full-error.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import Tabs from 'ui-kit/Tabs'
import { Tab } from 'ui-kit/Tabs/Tabs'

import {
  OLD_STEP_LIST,
  OLD_STEP_NAMES,
  STEP_ID_BANK_INFORMATIONS,
  STEP_ID_DETAILS,
  STEP_ID_INVOICES,
  STEP_NAMES,
} from './constants'
import styles from './ReimbursementsTabs.module.scss'

const ReimbursementsTabs = () => {
  const isNewBankDetailsJourneyEnabled = useActiveFeature(
    'WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'
  )
  const { selectedOfferer } = useReimbursementContext()

  const activeStep = useActiveStep(
    isNewBankDetailsJourneyEnabled ? STEP_NAMES : OLD_STEP_NAMES
  )
  const hasWarning =
    (selectedOfferer &&
      selectedOfferer?.venuesWithNonFreeOffersWithoutBankAccounts.length > 0) ??
    false

  const getSteps = () => {
    return [
      {
        id: STEP_ID_INVOICES,
        label: 'Justificatifs',
        url: '/remboursements',
      },
      {
        id: STEP_ID_DETAILS,
        label: 'Détails',
        url: '/remboursements/details',
      },
      {
        id: STEP_ID_BANK_INFORMATIONS,
        label: (
          <>
            Informations bancaires{' '}
            {hasWarning && (
              <SvgIcon
                src={fullErrorIcon}
                alt="Une action est requise dans cet onglet"
                width="20"
                className={styles['error-icon']}
              />
            )}
          </>
        ),
        url: '/remboursements/informations-bancaires',
      },
    ]
  }

  const tabs: Tab[] = (
    isNewBankDetailsJourneyEnabled ? getSteps() : OLD_STEP_LIST
  ).map(({ id, label, url }) => ({ key: id, label, url }))

  return <Tabs tabs={tabs} selectedKey={activeStep} />
}

export default ReimbursementsTabs
