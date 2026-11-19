import { useNavigate } from 'react-router'

import type { GetOffererResponseModel } from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { FinanceEvents } from '@/commons/core/FirebaseEvents/constants'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useActiveStep } from '@/commons/hooks/useActiveStep'
import fullErrorIcon from '@/icons/full-error.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'
import type { TabItem } from '@/ui-kit/Tabs/Tabs'
import { Tabs } from '@/ui-kit/Tabs/Tabs'

import {
  STEP_ID_BANK_INFORMATIONS,
  STEP_ID_INCOMES,
  STEP_ID_INVOICES,
  STEP_ID_SETTLEMENTS,
  STEP_NAMES,
} from './constants'
import styles from './ReimbursementsTabs.module.scss'

const URL_BY_STEP = {
  [STEP_ID_INVOICES]: '/administration/gestion-financiere/justificatifs',
  [STEP_ID_SETTLEMENTS]: '/administration/gestion-financiere/virements',
  [STEP_ID_BANK_INFORMATIONS]:
    '/administration/gestion-financiere/informations-bancaires',
  [STEP_ID_INCOMES]: '/administration/gestion-financiere/chiffre-d-affaires',
} as const

const EVENT_BY_STEP = {
  [STEP_ID_SETTLEMENTS]: FinanceEvents.CLICKED_SETTLEMENTS_TAB,
  [STEP_ID_INVOICES]: FinanceEvents.CLICKED_INVOICES_TAB,
  [STEP_ID_BANK_INFORMATIONS]: FinanceEvents.CLICKED_BANK_INFO_TAB,
  [STEP_ID_INCOMES]: FinanceEvents.CLICKED_REVENUE_TAB,
} as const

type Step = (typeof STEP_NAMES)[number]

type ReimbursementsTabsProps = {
  selectedOfferer: GetOffererResponseModel | null
}

export const ReimbursementsTabs = ({
  selectedOfferer,
}: ReimbursementsTabsProps) => {
  const navigate = useNavigate()
  const { logEvent } = useAnalytics()
  const isNewSettlementsActivated = useActiveFeature(
    'WIP_ENABLE_FINANCE_SETTLEMENTS'
  )
  const activeStep = useActiveStep([...STEP_NAMES])
  const hasWarning =
    (selectedOfferer &&
      (selectedOfferer.venuesWithNonFreeOffersWithoutBankAccounts.length > 0 ||
        selectedOfferer.hasBankAccountWithPendingCorrections)) ??
    false

  const getSteps = () => {
    const steps: Array<{
      id: Step
      label: React.ReactNode
    }> = [
      {
        id: STEP_ID_INVOICES,
        label: 'Justificatifs',
      },
      {
        id: STEP_ID_SETTLEMENTS,
        label: 'Virements',
      },
      {
        id: STEP_ID_BANK_INFORMATIONS,
        label: (
          <>
            Informations bancaires
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
      },
      {
        id: STEP_ID_INCOMES,
        label: "Chiffre d'affaires",
      },
    ]

    return steps.filter(
      (s) => isNewSettlementsActivated || s.id !== STEP_ID_SETTLEMENTS
    )
  }

  const tabs: TabItem<string>[] = getSteps().map(({ id, label }) => ({
    key: id,
    label,
    url: URL_BY_STEP[id],
  }))

  const onTabClick = (selectedTab: string) => {
    const event = EVENT_BY_STEP[selectedTab as Step]
    logEvent(event)
    const url = URL_BY_STEP[selectedTab as Step]
    navigate(url)
  }

  return (
    <Tabs
      items={tabs}
      selectedKey={activeStep}
      navLabel="Sous menu - Gestion financière"
      onClick={onTabClick}
    />
  )
}
