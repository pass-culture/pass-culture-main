import { GetOffererResponseModel } from 'apiClient/v1'
import { useActiveStep } from 'commons/hooks/useActiveStep'
import fullErrorIcon from 'icons/full-error.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { Tab, Tabs } from 'ui-kit/Tabs/Tabs'

import {
  STEP_ID_BANK_INFORMATIONS,
  STEP_ID_INCOMES,
  STEP_ID_INVOICES,
  STEP_NAMES,
} from './constants'
import styles from './ReimbursementsTabs.module.scss'

type ReimbursementsTabsProps = {
  selectedOfferer: GetOffererResponseModel | null
}

export const ReimbursementsTabs = ({
  selectedOfferer,
}: ReimbursementsTabsProps) => {
  const activeStep = useActiveStep(STEP_NAMES)
  const hasWarning =
    (selectedOfferer &&
      (selectedOfferer.venuesWithNonFreeOffersWithoutBankAccounts.length > 0 ||
        selectedOfferer.hasBankAccountWithPendingCorrections)) ??
    false

  const getSteps = () => {
    const steps = [
      {
        id: STEP_ID_INVOICES,
        label: 'Justificatifs',
        url: '/remboursements',
        isNew: false,
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
        isNew: false,
      },
      {
        id: STEP_ID_INCOMES,
        label: 'Chiffre d’affaires',
        url: '/remboursements/revenus',
        isNew: true,
      },
    ]

    return steps
  }

  const tabs: Tab[] = getSteps().map(({ id, label, url, isNew }) => ({
    key: id,
    label,
    url,
    isNew,
  }))

  return <Tabs tabs={tabs} selectedKey={activeStep} />
}
