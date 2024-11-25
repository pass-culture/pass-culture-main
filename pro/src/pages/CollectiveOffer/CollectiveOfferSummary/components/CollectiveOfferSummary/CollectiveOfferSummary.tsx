import {
  CollectiveOfferAllowedAction,
  CollectiveOfferStatus,
  CollectiveOfferTemplateAllowedAction,
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
} from 'apiClient/v1'
import {
  isCollectiveOffer,
  isCollectiveOfferTemplate,
} from 'commons/core/OfferEducational/types'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { isActionAllowedOnCollectiveOffer } from 'commons/utils/isActionAllowedOnCollectiveOffer'
import { AccessibilitySummarySection } from 'components/AccessibilitySummarySection/AccessibilitySummarySection'
import { SynchronizedProviderInformation } from 'components/IndividualOffer/SynchronisedProviderInfos/SynchronizedProviderInformation'
import { SummaryContent } from 'components/SummaryLayout/SummaryContent'
import { SummaryLayout } from 'components/SummaryLayout/SummaryLayout'
import { SummarySection } from 'components/SummaryLayout/SummarySection'

import styles from './CollectiveOfferSummary.module.scss'
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

  const areNewStatusesEnabled = useActiveFeature(
    'ENABLE_COLLECTIVE_NEW_STATUSES'
  )

  const isOfferTemplate = isCollectiveOfferTemplate(offer)

  const canEditOfferWithoutStatusFF =
    offer.status !== CollectiveOfferStatus.ARCHIVED &&
    (offerManuallyCreated || offer.isTemplate)

  const canEditDetails = areNewStatusesEnabled
    ? isActionAllowedOnCollectiveOffer(
        offer,
        offer.isTemplate
          ? CollectiveOfferTemplateAllowedAction.CAN_EDIT_DETAILS
          : CollectiveOfferAllowedAction.CAN_EDIT_DETAILS
      )
    : canEditOfferWithoutStatusFF

  const canEditDatesAndPrice = areNewStatusesEnabled
    ? [
        CollectiveOfferAllowedAction.CAN_EDIT_DATES,
        CollectiveOfferAllowedAction.CAN_EDIT_DISCOUNT,
      ].some((action) => isActionAllowedOnCollectiveOffer(offer, action))
    : canEditOfferWithoutStatusFF

  const canEditInstitution = areNewStatusesEnabled
    ? isActionAllowedOnCollectiveOffer(
        offer,
        CollectiveOfferAllowedAction.CAN_EDIT_INSTITUTION
      )
    : canEditOfferWithoutStatusFF

  return (
    <>
      <SummaryLayout>
        <SummaryContent fullWidth>
          {isCollectiveOffer(offer) && offer.provider?.name && (
            <div className={styles['banner-container']}>
              <SynchronizedProviderInformation
                providerName={offer.provider.name}
              />
            </div>
          )}
          <SummarySection
            title="Détails de l’offre"
            editLink={canEditDetails ? offerEditLink : null}
          >
            <CollectiveOfferVenueSection venue={offer.venue} />
            <CollectiveOfferTypeSection offer={offer} />
            <CollectiveOfferImagePreview offer={offer} />
            {isCollectiveOfferTemplate(offer) && (
              <CollectiveOfferDateSection offer={offer} />
            )}
            <CollectiveOfferLocationSection offer={offer} />
            {isCollectiveOfferTemplate(offer) && (
              <CollectiveOfferPriceSection offer={offer} />
            )}
            <CollectiveOfferParticipantSection students={offer.students} />
            <AccessibilitySummarySection
              accessibleItem={offer}
              accessibleWording="Votre offre est accessible aux publics en situation de handicap :"
            />
            <CollectiveOfferContactSection offer={offer} />
            {offer.bookingEmails.length > 0 && (
              <CollectiveOfferNotificationSection
                bookingEmails={offer.bookingEmails}
              />
            )}
          </SummarySection>
          {!isOfferTemplate && (
            <SummarySection
              title="Dates & Prix"
              editLink={canEditDatesAndPrice ? stockEditLink : null}
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
              editLink={canEditInstitution ? visibilityEditLink : null}
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
