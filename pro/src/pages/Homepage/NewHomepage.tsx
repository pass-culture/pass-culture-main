import { addDays, isBefore } from 'date-fns'
import { useId, useState } from 'react'

import {
  DMSApplicationstatus,
  type GetVenueResponseModel,
} from '@/apiClient/v1'
import { FrontendError } from '@/commons/errors/FrontendError'
import { handleUnexpectedError } from '@/commons/errors/handleUnexpectedError'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { getToday } from '@/commons/utils/date'
import { getLastCollectiveDmsApplication } from '@/commons/utils/getLastCollectiveDmsApplication'
import { CollectiveDmsTimeline } from '@/components/CollectiveDmsTimeline/CollectiveDmsTimeline'
import { CollectiveDmsTimelineVariant } from '@/components/CollectiveDmsTimeline/types'
import strokeWipIcon from '@/icons/stroke-wip.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'
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
import { CollectiveOffersCardsContainer } from './components/CollectiveOffersCardsContainer/CollectiveOffersCardsContainer'
import { EditoCard } from './components/EditoCard/EditoCard'
import { IncomeCard } from './components/IncomeCard/IncomeCard'
import { NewsletterCard } from './components/NewsletterCard/NewsletterCard'
import { OffersEmptyStateCard } from './components/OffersEmptyStateCard/OffersEmptyStateCard'
import { PartnerPageCard } from './components/PartnerPageCard/PartnerPageCard'
import { HomepageVariant, OffersCardVariant } from './components/types'
import { VenueValidationBanner } from './components/VenueValidationBanner/VenueValidationBanner'
import { WebinarCard } from './components/WebinarCard/WebinarCard'
import styles from './NewHomepage.module.scss'

export const NewHomepage = (): JSX.Element => {
  const selectedPartnerVenue: GetVenueResponseModel = useAppSelector(
    ensureSelectedPartnerVenue
  )

  const collectiveDmsApplication = getLastCollectiveDmsApplication(
    selectedPartnerVenue.collectiveDmsApplications ?? []
  )

  const hasIndividualTab = !!selectedPartnerVenue.hasNonDraftOffers
  const hasCollectiveTab =
    selectedPartnerVenue.allowedOnAdage || !!collectiveDmsApplication

  const [selectedTab, setSelectedTab] = useState(
    getInitialTab(selectedPartnerVenue.id, hasIndividualTab, hasCollectiveTab)
  )
  const individualId = useId()
  const collectiveId = useId()

  if (!hasIndividualTab && !hasCollectiveTab) {
    handleUnexpectedError(
      new FrontendError(
        'The venue must have at least one visible tab (individual or collective).'
      ),
      { isSilent: true }
    )
    return (
      <div className={styles['content']}>
        <SvgIcon className={styles['error-icon']} src={strokeWipIcon} alt="" />
        <h2 className={styles['title']}>Page indisponible</h2>
        <p className={styles['description']}>Veuillez réessayer plus tard</p>
      </div>
    )
  }

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
    onNewTabSelected(newSelectedTab, selectedPartnerVenue.id)
  }

  // Shared modules display conditions
  const shouldDisplayVenueValidationBanner = !selectedPartnerVenue.isValidated
  const shouldDisplayIncomeCard = selectedPartnerVenue.hasNonFreeOffers

  // Individual modules display conditions
  const shouldDisplayWebinarCard = isBefore(
    getToday(),
    addDays(selectedPartnerVenue.dateCreated, 31)
  )

  // Collective modules display conditions
  const hasRefusedDmsApplication =
    collectiveDmsApplication?.state === DMSApplicationstatus.REFUSE ||
    collectiveDmsApplication?.state === DMSApplicationstatus.SANS_SUITE

  const collectiveActivationDate =
    selectedPartnerVenue.adageInscriptionDate ??
    selectedPartnerVenue.dateCreated
  const shouldDisplayCollectiveWebinarCard = isBefore(
    getToday(),
    addDays(collectiveActivationDate, 31)
  )

  return (
    <>
      {shouldDisplayVenueValidationBanner && (
        <div className={styles['venue-validation-banner']}>
          <VenueValidationBanner />
        </div>
      )}
      {hasIndividualTab && hasCollectiveTab && (
        <Tabs
          type="tabs"
          navLabel="Sous menu - page d'accueil"
          items={tabs}
          selectedKey={selectedTab}
          onChange={handleTabChange}
        />
      )}
      {hasIndividualTab && selectedTab === TABS.INDIVIDUAL && (
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

          <div className={styles['main']}>
            <div>
              Activités sur vos offres individuelles
              <br />
              <b>Module gestion offres indivs</b>
            </div>
            <div>
              Evolution de consultation de vos offres
              <br />
              <b>Module statistiques</b>
            </div>
            <EditoCard
              canDisplayHighlights={selectedPartnerVenue.canDisplayHighlights}
              venueId={selectedPartnerVenue.id}
            />
          </div>

          <div className={styles['side']}>
            {shouldDisplayIncomeCard && (
              <IncomeCard
                venueId={selectedPartnerVenue.id}
                bankAccountStatus={
                  selectedPartnerVenue.bankAccountStatus ?? null
                }
              />
            )}
            <PartnerPageCard
              venueId={selectedPartnerVenue.id}
              venueName={selectedPartnerVenue.name}
              offererId={selectedPartnerVenue.managingOfferer.id}
              venueBannerUrl={selectedPartnerVenue.bannerUrl}
              venueBannerMeta={selectedPartnerVenue.bannerMeta}
              variant={HomepageVariant.INDIVIDUAL}
            />
            {shouldDisplayWebinarCard && (
              <WebinarCard variant={HomepageVariant.INDIVIDUAL} />
            )}
            <NewsletterCard />
          </div>
        </div>
      )}
      {hasCollectiveTab && selectedTab === TABS.COLLECTIVE && (
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
            {collectiveDmsApplication && (
              <CollectiveDmsTimeline
                collectiveDmsApplication={collectiveDmsApplication}
                hasAdageId={Boolean(selectedPartnerVenue.hasAdageId)}
                adageInscriptionDate={selectedPartnerVenue.adageInscriptionDate}
                variant={CollectiveDmsTimelineVariant.LITE}
              />
            )}
          </div>

          <div className={styles['main']}>
            {hasRefusedDmsApplication && (
              <OffersEmptyStateCard variant={OffersCardVariant.INDIVIDUAL} />
            )}
            {selectedPartnerVenue.allowedOnAdage && (
              <CollectiveOffersCardsContainer
                venueId={selectedPartnerVenue.id}
              />
            )}
          </div>

          <div className={styles['side']}>
            {selectedPartnerVenue.allowedOnAdage && (
              <>
                {shouldDisplayIncomeCard && (
                  <IncomeCard
                    venueId={selectedPartnerVenue.id}
                    bankAccountStatus={
                      selectedPartnerVenue.bankAccountStatus ?? null
                    }
                  />
                )}
                <PartnerPageCard
                  venueId={selectedPartnerVenue.id}
                  venueName={selectedPartnerVenue.name}
                  offererId={selectedPartnerVenue.managingOfferer.id}
                  venueBannerUrl={selectedPartnerVenue.bannerUrl}
                  venueBannerMeta={selectedPartnerVenue.bannerMeta}
                  variant={HomepageVariant.COLLECTIVE}
                />
                {shouldDisplayCollectiveWebinarCard && (
                  <WebinarCard variant={HomepageVariant.COLLECTIVE} />
                )}
                <NewsletterCard />
              </>
            )}
          </div>
        </div>
      )}
    </>
  )
}

// Below exports are used by react-router
// ts-unused-exports:disable-next-line
export const Component = NewHomepage
