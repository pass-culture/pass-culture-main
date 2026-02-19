import { addDays, isBefore } from 'date-fns'
import { useId, useState } from 'react'

import type { GetVenueResponseModel } from '@/apiClient/v1'
import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { ensureSelectedVenue } from '@/commons/store/user/selectors'
import { getToday } from '@/commons/utils/date'
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
  const selectedVenue: GetVenueResponseModel =
    useAppSelector(ensureSelectedVenue)
  const hasIndividual = !!selectedVenue.hasNonDraftOffers
  const hasCollective =
    selectedVenue.allowedOnAdage ||
    (selectedVenue.collectiveDmsApplications || []).length > 0

  const [selectedTab, setSelectedTab] = useState(
    getInitialTab(selectedVenue.id, hasIndividual, hasCollective)
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
    onNewTabSelected(newSelectedTab, selectedVenue.id)
  }

  // Shared modules display conditions
  const shouldDisplayHomologationBanner: boolean = !selectedVenue.isValidated
  const shouldDisplayBudgetCard: boolean = selectedVenue.hasNonFreeOffers

  // Individual modules display conditions
  const shouldDisplayWebinarCard: boolean = isBefore(
    getToday(),
    addDays(selectedVenue.dateCreated, 31)
  )

  return (
    <BasicLayout mainHeading={`Votre espace ${selectedVenue.publicName}`}>
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
            {shouldDisplayHomologationBanner && (
              <div>
                Votre structure est en cours de traitement par les équipes du
                pass Culture
                <br />
                <b>Banner Homologation</b>
              </div>
            )}
          </div>
          <div className={styles['main']}>
            <div>
              Activités sur vos offres individuelles
              <br />
              <b>Module gestion offre indivs</b>
            </div>
            <div>
              Evolution de consultation de vos offres
              <br />
              <b>Module statistiques</b>
            </div>
            <div>
              Comment valoriser vos offres auprès du jeune public ?
              <br />
              <b>Module Edito</b>
            </div>
          </div>
          <div className={styles['side']}>
            {shouldDisplayBudgetCard && (
              <div>
                Remboursement
                <br />
                <b>Module Budget</b>
              </div>
            )}
            <div>
              Votre page sur l’application
              <br />
              <b>Module page partenaire</b>
            </div>
            {shouldDisplayWebinarCard && (
              <div>
                Participer à nos webinaires sur la part individuelle !
                <br />
                <b>Module Webinaires indiv</b>
              </div>
            )}
            <div>
              Suivez notre actualité !
              <br />
              <b>Module Newsletter</b>
            </div>
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
