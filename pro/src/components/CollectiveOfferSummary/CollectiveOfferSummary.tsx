import React from 'react'

import { SummaryLayout } from 'components/SummaryLayout'
import {
  CollectiveOffer,
  CollectiveOfferTemplate,
  EducationalCategories,
} from 'core/OfferEducational'

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

interface ICollectiveOfferSummaryProps {
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
}: ICollectiveOfferSummaryProps) => {
  return (
    <>
      <SummaryLayout>
        <SummaryLayout.Content fullWidth>
          <SummaryLayout.Section
            title="Détails de l’offre"
            editLink={offerEditLink}
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
            <SummaryLayout.Section title="Date & Prix" editLink={stockEditLink}>
              <CollectiveOfferStockSection
                stock={offer.collectiveStock}
                venueDepartmentCode={offer.venue.departementCode}
              />
            </SummaryLayout.Section>
          )}
          {!offer.isTemplate && (
            <SummaryLayout.Section
              title="Visibilité"
              editLink={visibilityEditLink}
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
