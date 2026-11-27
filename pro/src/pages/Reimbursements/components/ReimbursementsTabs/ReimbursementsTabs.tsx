import type { GetOffererResponseModel } from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { useActiveStep } from '@/commons/hooks/useActiveStep'
import { ButtonIconColor } from '@/design-system/Button/types'
import fullErrorIcon from '@/icons/full-error.svg'
import type { TabItem } from '@/ui-kit/Tabs/Tabs'
import { Tabs } from '@/ui-kit/Tabs/Tabs'

import {
  EVENT_BY_TAB,
  TAB_ID_BANK_INFORMATIONS,
  TAB_ID_INCOMES,
  TAB_ID_INVOICES,
  TAB_ID_SETTLEMENTS,
  TAB_NAMES,
} from './constants'

type ReimbursementsTabsProps = {
  selectedOfferer: GetOffererResponseModel | null
}

export const ReimbursementsTabs = ({
  selectedOfferer,
}: ReimbursementsTabsProps) => {
  const { logEvent } = useAnalytics()

  const activeTab = useActiveStep([...TAB_NAMES])
  const hasWarning =
    (selectedOfferer &&
      (selectedOfferer.venuesWithNonFreeOffersWithoutBankAccounts.length > 0 ||
        selectedOfferer.hasBankAccountWithPendingCorrections)) ??
    false

  const tabs: TabItem<string>[] = [
    {
      key: TAB_ID_SETTLEMENTS,
      label: 'Virements',
      url: '/administration/gestion-financiere/virements',
    },
    {
      key: TAB_ID_INVOICES,
      label: 'Justificatifs',
      url: '/administration/gestion-financiere/justificatifs',
    },
    {
      key: TAB_ID_BANK_INFORMATIONS,
      label: 'Informations bancaires',
      url: '/administration/gestion-financiere/informations-bancaires',
      ...(hasWarning && {
        icon: fullErrorIcon,
        iconAlt: 'Une action est requise dans cet onglet',
        iconColor: ButtonIconColor.ERROR,
      }),
    },
    {
      key: TAB_ID_INCOMES,
      label: "Chiffre d'affaires",
      url: '/administration/gestion-financiere/chiffre-d-affaires',
    },
  ]

  const onTabClick = (selectedTab: string) => {
    const event = EVENT_BY_TAB[selectedTab as TAB_NAMES]
    logEvent(event)
  }

  return (
    <Tabs
      items={tabs}
      selectedKey={activeTab}
      navLabel="Sous menu - Gestion financière"
      onClick={onTabClick}
    />
  )
}
