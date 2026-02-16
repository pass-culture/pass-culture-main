import { useId, useState } from 'react'

import type { GetVenueResponseModel } from '@/apiClient/v1'
import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import {
  getPanelId,
  getTabId,
  type TabItem,
} from '@/ui-kit/Tabs/TabItems/TabItems'
import { Tabs } from '@/ui-kit/Tabs/Tabs'

import {
  getInitialTab,
  onNewTabSelected,
  TABS,
  type TabKey,
} from './commons/utils'
import styles from './NewHomepage.module.scss'

export const NewHomepage = (): JSX.Element => {
  const selectedVenue: GetVenueResponseModel | null = useAppSelector(
    (state) => state.user.selectedVenue
  )
  const hasIndividual = !!selectedVenue?.hasNonDraftOffers
  const hasCollective =
    selectedVenue?.allowedOnAdage ||
    (selectedVenue?.collectiveDmsApplications || []).length > 0

  const [selectedTab, setSelectedTab] = useState(
    getInitialTab(selectedVenue?.id ?? null, hasIndividual, hasCollective)
  )
  const individualId = useId()
  const collectiveId = useId()

  const tabs: TabItem<TabKey>[] = [
    {
      key: TABS.INDIVIDUAL,
      label: 'Individuel',
      baseId: individualId,
    },
    {
      key: TABS.COLLECTIVE,
      label: 'Collectif',
      baseId: collectiveId,
    },
  ]

  const handleTabChange = (newSelectedTab: TabKey) => {
    setSelectedTab(newSelectedTab)
    onNewTabSelected(newSelectedTab, selectedVenue?.id ?? null)
  }

  return (
    <BasicLayout mainHeading={`Votre espace ${selectedVenue?.publicName}`}>
      {hasIndividual && hasCollective && (
        <Tabs
          type="tabs"
          navLabel="Sous menu - page d'accueil"
          items={tabs}
          selectedKey={selectedTab}
          onChange={handleTabChange}
        />
      )}
      {hasIndividual && selectedTab === TABS.INDIVIDUAL && (
        <div
          id={getPanelId(individualId)}
          role="tabpanel"
          className={styles['container']}
          aria-labelledby={getTabId(individualId)}
          aria-describedby={`description-${individualId}`}
          tabIndex={selectedTab === TABS.INDIVIDUAL ? 0 : -1}
        >
          <span
            id={`description-${individualId}`}
            className={styles['visually-hidden']}
          >
            Page d'accueil - part individuelle
          </span>
          <div className={styles['top']}>
            <div>Banner indiv</div>
          </div>
          <div className={styles['main']}>
            <div>Liste des offres indiv</div>
            <div>Stats de consult</div>
            <div>Edito</div>
          </div>
          <div className={styles['side']}>
            <div>Page partenaire</div>
            <div>Newsletter</div>
            <div>Budget €€€</div>
          </div>
        </div>
      )}
      {hasCollective && selectedTab === TABS.COLLECTIVE && (
        <div
          id={getPanelId(collectiveId)}
          role="tabpanel"
          className={styles['container']}
          aria-labelledby={getTabId(collectiveId)}
          aria-describedby={`description-${collectiveId}`}
          tabIndex={selectedTab === TABS.COLLECTIVE ? 0 : -1}
          hidden={selectedTab !== TABS.COLLECTIVE}
        >
          <span
            id={`description-${collectiveId}`}
            className={styles['visually-hidden']}
          >
            Page d'accueil - part collective
          </span>
          <div className={styles['top']}>
            <div>Banner collective</div>
          </div>
          <div className={styles['main']}>
            <div>Liste des offres collectives vitrines</div>
            <div>Empty state des offres réservables</div>
          </div>
          <div className={styles['side']}>
            <div>Page partenaire</div>
            <div>Newsletter</div>
            <div>Budget €€€</div>
          </div>
        </div>
      )}
    </BasicLayout>
  )
}

// Below exports are used by react-router
// ts-unused-exports:disable-next-line
export const Component = NewHomepage
