import { useActiveStep } from '@/commons/hooks/useActiveStep'
import type { NavLinkItem } from '@/ui-kit/Tabs/NavLinkItems/NavLinkItems'
import { Tabs } from '@/ui-kit/Tabs/Tabs'

import {
  STEP_ID_GENERAL_INFORMATIONS,
  STEP_ID_NOTIFICATIONS,
  STEP_ID_PROVIDERS,
  STEP_NAMES,
} from './constants'

export const SettingsTabs = () => {
  const activeStep = useActiveStep(STEP_NAMES)

  const tabs: NavLinkItem<string>[] = [
    {
      key: STEP_ID_GENERAL_INFORMATIONS,
      label: 'Informations générales',
      url: '/parametres/informations-generales',
    },
    {
      key: STEP_ID_NOTIFICATIONS,
      label: 'Notifications',
      url: '/parametres/notifications',
    },
    {
      key: STEP_ID_PROVIDERS,
      label: 'Synchronisations',
      url: '/parametres/synchronisations',
    },
  ]

  return (
    <Tabs
      type="links"
      items={tabs}
      selectedKey={activeStep}
      navLabel="Sous menu - Paramètres"
    />
  )
}
