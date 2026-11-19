import cn from 'classnames'
import { useNavigate } from 'react-router'

import type { TabItem } from '@/ui-kit/Tabs/Tabs'
import { Tabs } from '@/ui-kit/Tabs/Tabs'

import styles from './CollectiveOfferNavigation.module.scss'
import { CollectiveOfferStep } from './constants'

interface CollectiveOfferEditionNavigationProps {
  activeStep: CollectiveOfferStep
  offerId?: number
}

export const CollectiveOfferEditionNavigation = ({
  activeStep,
  offerId = 0,
}: CollectiveOfferEditionNavigationProps): JSX.Element => {
  const navigate = useNavigate()

  const tabs: TabItem<string>[] = [
    {
      key: CollectiveOfferStep.DETAILS,
      label: "Détails de l'offre",
      url: `/offre/${offerId}/collectif/edition`,
    },
    {
      key: CollectiveOfferStep.STOCKS,
      label: 'Dates et prix',
      url: `/offre/${offerId}/collectif/stocks/edition`,
    },
    {
      key: CollectiveOfferStep.INFORMATION,
      label: 'Informations pratiques',
      url: `/offre/${offerId}/collectif/informations-pratiques/edition`,
    },
    {
      key: CollectiveOfferStep.INSTITUTION,
      label: 'Établissement et enseignant',
      url: `/offre/${offerId}/collectif/etablissement/edition`,
    },
  ]

  const allTabs = tabs.map((t) => t.key)

  const handleTabClick = (selectedStep: string) => {
    const tab = tabs.find((t) => t.key === selectedStep)
    if (tab?.url) {
      navigate(tab.url)
    }
  }

  return (
    <Tabs
      items={tabs}
      selectedKey={activeStep}
      navLabel="Sous menu - offre collective"
      onClick={handleTabClick}
      className={cn(styles['tabs'], {
        [styles['tabs-active']]: allTabs.includes(activeStep),
      })}
    />
  )
}
