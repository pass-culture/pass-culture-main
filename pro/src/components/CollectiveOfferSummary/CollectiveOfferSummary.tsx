import React from 'react'

import BannerPublicApi from 'components/Banner/BannerPublicApi'
import { SummaryLayout } from 'components/SummaryLayout'
import {
  CollectiveOffer,
  CollectiveOfferTemplate,
  EducationalCategories,
  isCollectiveOffer,
} from 'core/OfferEducational'

import styles from './CollectiveOfferSummary.module.scss'
import CollectiveOfferAccessibilitySection from './components/CollectiveOfferAccessibilitySection'
import CollectiveOfferContactSection from './components/CollectiveOfferContactSection'
import CollectiveOfferImagePreview from './components/CollectiveOfferImagePreview'
import CollectiveOfferNotificationSection from './components/CollectiveOfferNotificationSection'
import CollectiveOfferParticipantSection from './components/CollectiveOfferParticipantSection'
import CollectiveOfferPracticalInformation from './components/CollectiveOfferPracticalInformation'
import CollectiveOfferStockSection from './components/CollectiveOfferStockSection'
import CollectiveOfferTypeSection from './components/CollectiveOfferTypeSection'
import CollectiveOfferVenueSection from './components/CollectiveOfferVenueSection'
import CollectiveOfferVisibilitySection from './components/CollectiveOfferVisibilitySection'

export interface CollectiveOfferSummaryProps {
  offer: CollectiveOfferTemplate | CollectiveOffer
  categories: EducationalCategories
  offerEditLink?: string
  stockEditLink?: string
  visibilityEditLink?: string
}

const CollectiveOfferSummary = ({
  offer,
  categories,
  offerEditLink,
  stockEditLink,
  visibilityEditLink,
}: CollectiveOfferSummaryProps) => {
  const offerManuallyCreated = isCollectiveOffer(offer) && !offer.isPublicApi

  return (
    <>
      <SummaryLayout>
        <SummaryLayout.Content fullWidth>
          {isCollectiveOffer(offer) && offer.isPublicApi && (
            <BannerPublicApi className={styles['banner-space']}>
              Offre créée par votre outil de billetterie via l’API offres
              collectives
            </BannerPublicApi>
          )}
          <SummaryLayout.Section
            title="Détails de l’offre"
            editLink={
              offerManuallyCreated || offer.isTemplate ? offerEditLink : ''
            }
          >
            <CollectiveOfferVenueSection venue={offer.venue} />
            <CollectiveOfferTypeSection offer={offer} categories={categories} />
            <CollectiveOfferImagePreview offer={offer} />
            <CollectiveOfferPracticalInformation offer={offer} />
            <CollectiveOfferParticipantSection students={offer.students} />
            <CollectiveOfferAccessibilitySection offer={offer} />
            <CollectiveOfferContactSection
              phone={offer.contactPhone}
              email={offer.contactEmail}
            />
            {offer.bookingEmails.length > 0 && (
              <CollectiveOfferNotificationSection
                bookingEmails={offer.bookingEmails}
              />
            )}
          </SummaryLayout.Section>

          {!offer.isTemplate && (
            <SummaryLayout.Section
              title="Date & Prix"
              editLink={
                offerManuallyCreated || offer.isTemplate ? stockEditLink : ''
              }
            >
              <CollectiveOfferStockSection
                stock={offer.collectiveStock}
                venueDepartmentCode={offer.venue.departementCode}
              />
            </SummaryLayout.Section>
          )}

          {!offer.isTemplate && (
            <SummaryLayout.Section
              title="Visibilité"
              editLink={
                offerManuallyCreated || offer.isTemplate
                  ? visibilityEditLink
                  : ''
              }
            >
              <CollectiveOfferVisibilitySection
                institution={offer.institution}
                teacher={offer.teacher}
              />
            </SummaryLayout.Section>
          )}
        </SummaryLayout.Content>
      </SummaryLayout>
    </>
  )
}

export default CollectiveOfferSummary
