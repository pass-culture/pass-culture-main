import React from 'react'

import {
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
} from 'apiClient/v1'
import { SummaryContent } from 'components/SummaryLayout/SummaryContent'
import { SummaryLayout } from 'components/SummaryLayout/SummaryLayout'
import { SummarySection } from 'components/SummaryLayout/SummarySection'
import {
  isCollectiveOffer,
  isCollectiveOfferTemplate,
} from 'core/OfferEducational/types'
import { SynchronizedProviderInformation } from 'screens/IndividualOffer/SynchronisedProviderInfos/SynchronizedProviderInformation'

import { CollectiveOfferAccessibilitySection } from './components/CollectiveOfferAccessibilitySection'
import { CollectiveOfferContactSection } from './components/CollectiveOfferContactSection'
import { CollectiveOfferDateSection } from './components/CollectiveOfferDateSection'
import { CollectiveOfferImagePreview } from './components/CollectiveOfferImagePreview'
import { CollectiveOfferLocationSection } from './components/CollectiveOfferLocationSection'
import { CollectiveOfferNotificationSection } from './components/CollectiveOfferNotificationSection'
import { CollectiveOfferParticipantSection } from './components/CollectiveOfferParticipantSection'
import { CollectiveOfferPriceSection } from './components/CollectiveOfferPriceSection'
import { CollectiveOfferStockSection } from './components/CollectiveOfferStockSection'
import { CollectiveOfferTypeSection } from './components/CollectiveOfferTypeSection'
import { CollectiveOfferVenueSection } from './components/CollectiveOfferVenueSection'
import { CollectiveOfferVisibilitySection } from './components/CollectiveOfferVisibilitySection'

export interface CollectiveOfferSummaryProps {
  offer:
    | GetCollectiveOfferTemplateResponseModel
    | GetCollectiveOfferResponseModel
  offerEditLink?: string
  stockEditLink?: string
  visibilityEditLink?: string
}

export const CollectiveOfferSummary = ({
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
          {isCollectiveOffer(offer) && offer.provider?.name && (
            <SynchronizedProviderInformation
              providerName={offer.provider.name}
            />
          )}
          <SummarySection
            title="Détails de l’offre"
            editLink={
              offerManuallyCreated || offer.isTemplate ? offerEditLink : null
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
            <CollectiveOfferContactSection offer={offer} />
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
                offerManuallyCreated || offer.isTemplate ? stockEditLink : null
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
                  : null
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
