import React from 'react'

import BannerPublicApi from 'components/Banner/BannerPublicApi'
import { SummaryContent } from 'components/SummaryLayout/SummaryContent'
import { SummaryLayout } from 'components/SummaryLayout/SummaryLayout'
import { SummarySection } from 'components/SummaryLayout/SummarySection'
import {
  CollectiveOffer,
  CollectiveOfferTemplate,
  isCollectiveOffer,
  isCollectiveOfferTemplate,
} from 'core/OfferEducational'

import styles from './CollectiveOfferSummary.module.scss'
import CollectiveOfferAccessibilitySection from './components/CollectiveOfferAccessibilitySection'
import CollectiveOfferContactSection from './components/CollectiveOfferContactSection'
import CollectiveOfferDateSection from './components/CollectiveOfferDateSection/CollectiveOfferDateSection'
import CollectiveOfferImagePreview from './components/CollectiveOfferImagePreview'
import CollectiveOfferLocationSection from './components/CollectiveOfferLocationSection/CollectiveOfferLocationSection'
import CollectiveOfferNotificationSection from './components/CollectiveOfferNotificationSection'
import CollectiveOfferParticipantSection from './components/CollectiveOfferParticipantSection'
import CollectiveOfferPriceSection from './components/CollectiveOfferPriceSection/CollectiveOfferPriceSection'
import CollectiveOfferStockSection from './components/CollectiveOfferStockSection'
import CollectiveOfferTypeSection from './components/CollectiveOfferTypeSection/CollectiveOfferTypeSection'
import CollectiveOfferVenueSection from './components/CollectiveOfferVenueSection'
import CollectiveOfferVisibilitySection from './components/CollectiveOfferVisibilitySection'

export interface CollectiveOfferSummaryProps {
  offer: CollectiveOfferTemplate | CollectiveOffer
  offerEditLink?: string
  stockEditLink?: string
  visibilityEditLink?: string
}

const CollectiveOfferSummary = ({
  offer,
  offerEditLink,
  stockEditLink,
  visibilityEditLink,
}: CollectiveOfferSummaryProps) => {
  const offerManuallyCreated = isCollectiveOffer(offer) && !offer.isPublicApi

  const isOfferTemplate = isCollectiveOfferTemplate(offer)
  return (
    <>
      <SummaryLayout>
        <SummaryContent fullWidth>
          {isCollectiveOffer(offer) && offer.isPublicApi && (
            <BannerPublicApi className={styles['banner-space']}>
              Offre créée par votre outil de billetterie via l’API offres
              collectives
            </BannerPublicApi>
          )}
          <SummarySection
            title="Détails de l’offre"
            editLink={
              offerManuallyCreated || offer.isTemplate ? offerEditLink : ''
            }
          >
            <CollectiveOfferVenueSection venue={offer.venue} />
            <CollectiveOfferTypeSection offer={offer} />
            <CollectiveOfferImagePreview offer={offer} />
            {offer.isTemplate && <CollectiveOfferDateSection offer={offer} />}
            <CollectiveOfferLocationSection offer={offer} />
            {offer.isTemplate && <CollectiveOfferPriceSection offer={offer} />}
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
          </SummarySection>

          {!isOfferTemplate && (
            <SummarySection
              title="Date & Prix"
              editLink={
                offerManuallyCreated || offer.isTemplate ? stockEditLink : ''
              }
            >
              <CollectiveOfferStockSection
                stock={offer.collectiveStock}
                venueDepartmentCode={offer.venue.departementCode}
              />
            </SummarySection>
          )}

          {!isOfferTemplate && (
            <SummarySection
              title={'Établissement et enseignant'}
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
            </SummarySection>
          )}
        </SummaryContent>
      </SummaryLayout>
    </>
  )
}

export default CollectiveOfferSummary
