import cn from 'classnames'

import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import type { NavLinkItem } from '@/ui-kit/Tabs/NavLinkItems/NavLinkItems'
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
  const isNewCollectivePriceEnabled = useActiveFeature(
    'WIP_ENABLE_NEW_COLLECTIVE_PRICE_DETAILS'
  )

  let tabs: NavLinkItem<string>[] = [
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

  if (!isNewCollectivePriceEnabled) {
    tabs = tabs.filter((s) => s.key !== CollectiveOfferStep.INFORMATION)
  }

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
