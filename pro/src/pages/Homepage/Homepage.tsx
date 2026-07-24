import { addDays, isBefore } from 'date-fns'
import { useId, useState } from 'react'

import {
  DMSApplicationstatus,
  type GetVenueResponseModel,
} from '@/apiClient/v1'
import { MainHeading } from '@/app/App/layouts/components/MainHeading/MainHeading'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { getToday } from '@/commons/utils/date'
import { withVenueHelpers } from '@/commons/utils/withVenueHelpers'
import { CollectiveDmsTimeline } from '@/components/CollectiveDmsTimeline/CollectiveDmsTimeline'
import { CollectiveDmsTimelineVariant } from '@/components/CollectiveDmsTimeline/types'
import { OnboardingOffersChoice } from '@/components/OnboardingOffersChoice/OnboardingOffersChoice'
import { Banner, BannerVariants } from '@/design-system/Banner/Banner'
import { Button } from '@/design-system/Button/Button'
import { ButtonSize, ButtonVariant } from '@/design-system/Button/types'
import { BaseDialog } from '@/ui-kit/BaseDialog/BaseDialog'
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
import { IndividualOffersCard } from './components/IndividualOffersCard/IndividualOffersCard'
import { NewsletterCard } from './components/NewsletterCard/NewsletterCard'
import { OffersEmptyStateCard } from './components/OffersEmptyStateCard/OffersEmptyStateCard'
import { PartnerPageCard } from './components/PartnerPageCard/PartnerPageCard'
import { StatsCard } from './components/StatsCard/StatsCard'
import { HomepageVariant, OffersCardVariant } from './components/types'
import { VenueValidationBanner } from './components/VenueValidationBanner/VenueValidationBanner'
import { WebinarCard } from './components/WebinarCard/WebinarCard'
import styles from './Homepage.module.scss'

export const Homepage = (): JSX.Element => {
  const selectedPartnerVenue: GetVenueResponseModel = useAppSelector(
    ensureSelectedPartnerVenue
  )

  const collectiveDmsApplication =
    selectedPartnerVenue.lastCollectiveDmsApplication

  const hasIndividualTab = !!selectedPartnerVenue.hasNonDraftOffers
  const hasCollectiveTab =
    selectedPartnerVenue.allowedOnAdage || !!collectiveDmsApplication

  const [selectedTab, setSelectedTab] = useState(
    getInitialTab(selectedPartnerVenue.id, hasIndividualTab, hasCollectiveTab)
  )
  const individualId = useId()
  const collectiveId = useId()

  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [isDetailedDialogOpen, setIsDetailedDialogOpen] = useState(false)

  if (!hasIndividualTab && !hasCollectiveTab) {
    return (
      <div className={styles['onboarding-container']}>
        <h2 className={styles['onboarding-title']}>
          Diffusez votre première offre et pilotez ici votre activité !
        </h2>
        <OnboardingOffersChoice hideSkipOnboardingLink />
      </div>
    )
  }

  const isVenueClosed = withVenueHelpers(selectedPartnerVenue).isClosed
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
      <div className={styles['open-modal-buttons']}>
        <Button
          label="Ouvrir une modale simple"
          onClick={() => {
            setIsDialogOpen(true)
          }}
          variant={ButtonVariant.SECONDARY}
          size={ButtonSize.SMALL}
        />
        <Button
          label="Ouvrir une modale detailed"
          onClick={() => {
            setIsDetailedDialogOpen(true)
          }}
          variant={ButtonVariant.SECONDARY}
          size={ButtonSize.SMALL}
        />
      </div>

      {/* Simple modal example */}
      <BaseDialog
        isOpen={isDialogOpen}
        onClose={() => {
          setIsDialogOpen(false)
        }}
      >
        <div className={styles['dialog-content-simple']}>
          <h1>Modale simple</h1>
          <p>
            Voici le contenu d'une modale simple implémentée par dessus le
            composant utilitaire <code>&lt;BaseDialog&gt;</code>, lui-même basé
            sur la balise HTML5 standard <code>&lt;dialog&gt;</code>
          </p>
          <p>
            Second paragraphe contenant un{' '}
            <Button
              as="a"
              label="lien focusable"
              to="https://google.com"
              isExternal
              opensInNewTab
              variant={ButtonVariant.TERTIARY}
            />
          </p>
          <Button
            label="Fermer la modale"
            onClick={() => {
              setIsDialogOpen(false)
            }}
          >
            Close Dialog
          </Button>
        </div>
      </BaseDialog>

      {/* Detailed modal example */}
      <BaseDialog
        isOpen={isDetailedDialogOpen}
        onClose={() => {
          setIsDetailedDialogOpen(false)
        }}
      >
        <div className={styles['dialog-content-detailed']}>
          <h1>Modale detailed</h1>
          <p>
            Voici le contenu d'une modale detailed implémentée par dessus le
            composant utilitaire <code>&lt;BaseDialog&gt;</code>, lui-même basé
            sur la balise HTML5 standard <code>&lt;dialog&gt;</code>
          </p>
          <Button
            label="Ré-ouvrir la modale simple par dessus"
            variant={ButtonVariant.SECONDARY}
            size={ButtonSize.SMALL}
            onClick={() => {
              setIsDialogOpen(true)
            }}
          />
          <div className={styles['action-buttons']}>
            <Button
              label="Annuler"
              variant={ButtonVariant.SECONDARY}
              onClick={() => {
                setIsDetailedDialogOpen(false)
              }}
            />
            <Button
              label="Confirmer"
              onClick={() => {
                setIsDetailedDialogOpen(false)
              }}
            />
          </div>
        </div>
      </BaseDialog>

      <MainHeading
        mainHeading={`Votre espace ${selectedPartnerVenue.publicName}`}
      />
      {withVenueHelpers(selectedPartnerVenue).isClosed && (
        <div className={styles['venue-banner']}>
          <Banner variant={BannerVariants.ERROR} title="Structure fermée" />
        </div>
      )}
      {shouldDisplayVenueValidationBanner && (
        <div className={styles['venue-banner']}>
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
            <IndividualOffersCard
              isReadOnly={isVenueClosed}
              venueId={selectedPartnerVenue.id}
              venueDepartmentCode={
                selectedPartnerVenue.location?.departmentCode
              }
            />
            <StatsCard venue={selectedPartnerVenue} />
            <EditoCard
              canDisplayHighlights={selectedPartnerVenue.canDisplayHighlights}
              isReadOnly={isVenueClosed}
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
              isReadOnly={isVenueClosed}
              venueId={selectedPartnerVenue.id}
              venueName={selectedPartnerVenue.publicName}
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
              <OffersEmptyStateCard
                isReadOnly={isVenueClosed}
                variant={OffersCardVariant.INDIVIDUAL}
              />
            )}
            {selectedPartnerVenue.allowedOnAdage && (
              <CollectiveOffersCardsContainer
                isReadOnly={isVenueClosed}
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
                  isReadOnly={isVenueClosed}
                  venueId={selectedPartnerVenue.id}
                  venueName={selectedPartnerVenue.publicName}
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
export const Component = Homepage
