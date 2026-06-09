import cn from 'classnames'

import type { NavLinkItem } from '@/ui-kit/Tabs/NavLinkItems/NavLinkItems'
import { Tabs } from '@/ui-kit/Tabs/Tabs'

import { CollectiveOfferStep } from './CollectiveOfferCreationNavigation'
import styles from './CollectiveOfferNavigation.module.scss'

export interface CollectiveOfferEditionNavigationProps {
  activeStep: CollectiveOfferStep
  offerId?: number
}

export const CollectiveOfferEditionNavigation = ({
  activeStep,
  offerId = 0,
}: CollectiveOfferEditionNavigationProps): JSX.Element => {
  const tabs: NavLinkItem<string>[] = [
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
      key: CollectiveOfferStep.INSTITUTION,
      label: 'Établissement et enseignant',
      url: `/offre/${offerId}/collectif/etablissement/edition`,
    },
  ]

  const allTabs = tabs.map((t) => t.key)

  return (
    <Tabs
      type="links"
      items={tabs}
      selectedKey={activeStep}
      navLabel="Sous menu - offre collective"
      className={cn(styles['tabs'], {
        [styles['tabs-active']]: allTabs.includes(activeStep),
      })}
    />
  )
}
