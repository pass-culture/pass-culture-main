import { useId, useState } from 'react'

import type { GetVenueResponseModel } from '@/apiClient/v1'
import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import type { TabItem } from '@/ui-kit/Tabs/TabItems/TabItems'
import { Tabs } from '@/ui-kit/Tabs/Tabs'

export const NewHomepage = (): JSX.Element => {
  const selectedVenue: GetVenueResponseModel | null = useAppSelector(
    (state) => state.user.selectedVenue
  )
  const hasIndividual = selectedVenue?.hasActiveIndividualOffer
  const hasCollective =
    selectedVenue?.allowedOnAdage ||
    (selectedVenue?.collectiveDmsApplications || []).length > 0

  const [selectedTab, setSelectedTab] = useState(
    hasIndividual ? 'tab-individual' : 'tab-collective'
  )
  const individualId = useId()
  const collectiveId = useId()

  const tabs: TabItem[] = [
    {
      key: 'tab-individual',
      label: 'Individuel',
      tabId: `tab-${individualId}`,
      panelId: `panel-${individualId}`,
    },
    {
      key: 'tab-collective',
      label: 'Collectif',
      tabId: `tab-${collectiveId}`,
      panelId: `panel-${collectiveId}`,
    },
  ]

  return (
    <BasicLayout mainHeading={`Votre espace ${selectedVenue?.publicName}`}>
      {hasIndividual && hasCollective && (
        <Tabs
          type="tabs"
          navLabel="Sous menu - page d'accueil"
          items={tabs}
          selectedKey={selectedTab}
          onChange={setSelectedTab}
        />
      )}
      {hasIndividual && (
        <div
          id={`panel-${individualId}`}
          role="tabpanel"
          aria-labelledby={`tab-${individualId}`}
          tabIndex={selectedTab === 'tab-individual' ? 0 : -1}
          hidden={selectedTab !== 'tab-individual'}
        >
          <p>Bienvenue sur l'accueil individuel</p>
        </div>
      )}
      {hasCollective && (
        <div
          id={`panel-${collectiveId}`}
          role="tabpanel"
          aria-labelledby={`tab-${collectiveId}`}
          tabIndex={selectedTab === 'tab-collective' ? 0 : -1}
          hidden={selectedTab !== 'tab-collective'}
        >
          <p>Bienvenue sur l'accueil collectif</p>
        </div>
      )}
    </BasicLayout>
  )
}

// Below exports are used by react-router
// ts-unused-exports:disable-next-line
export const Component = NewHomepage
