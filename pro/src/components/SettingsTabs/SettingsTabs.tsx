import { useNavigate } from 'react-router'

import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useActiveStep } from '@/commons/hooks/useActiveStep'
import type { TabItem } from '@/ui-kit/Tabs/Tabs'
import { Tabs } from '@/ui-kit/Tabs/Tabs'

import {
  STEP_ID_GENERAL_INFORMATIONS,
  STEP_ID_MANAGEMENT,
  STEP_ID_NOTIFICATIONS,
  STEP_ID_PROVIDERS,
  STEP_NAMES,
} from './constants'

const URL_BY_STEP = {
  [STEP_ID_GENERAL_INFORMATIONS]: '/parametres/informations-generales',
  [STEP_ID_NOTIFICATIONS]: '/parametres/notifications',
  [STEP_ID_PROVIDERS]: '/parametres/synchronisations',
  [STEP_ID_MANAGEMENT]: '/parametres/gestion-structure',
} as const

export const SettingsTabs = () => {
  const navigate = useNavigate()
  const activeStep = useActiveStep(STEP_NAMES)
  const isCloseVenueEnabled = useActiveFeature('WIP_CLOSE_VENUE')

  const tabs: TabItem<string>[] = [
    {
      key: STEP_ID_GENERAL_INFORMATIONS,
      label: 'Informations générales',
      url: URL_BY_STEP[STEP_ID_GENERAL_INFORMATIONS],
    },
    {
      key: STEP_ID_NOTIFICATIONS,
      label: 'Notifications',
      url: URL_BY_STEP[STEP_ID_NOTIFICATIONS],
    },
    {
      key: STEP_ID_PROVIDERS,
      label: 'Synchronisations',
      url: URL_BY_STEP[STEP_ID_PROVIDERS],
    },
  ]

  if (isCloseVenueEnabled) {
    tabs.push({
      key: STEP_ID_MANAGEMENT,
      label: 'Gestion de la structure',
      url: URL_BY_STEP[STEP_ID_MANAGEMENT],
    })
  }

  const handleTabClick = (selectedStep: string) => {
    const url = URL_BY_STEP[selectedStep as keyof typeof URL_BY_STEP]
    if (url) {
      navigate(url)
    }
  }

  return (
    <Tabs
      items={tabs}
      selectedKey={activeStep}
      navLabel="Sous menu - Paramètres"
      onClick={handleTabClick}
    />
  )
}
