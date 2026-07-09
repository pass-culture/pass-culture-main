import type {
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
} from '@/apiClient/v1'
import {
  isCollectiveOffer,
  isCollectiveOfferTemplate,
} from '@/commons/core/OfferEducational/types'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import {
  isCollectiveInstitutionEditable,
  isCollectiveOfferDetailsEditable,
  isCollectiveStockEditable,
} from '@/commons/utils/isActionAllowedOnCollectiveOffer'
import { withVenueHelpers } from '@/commons/utils/withVenueHelpers'
import { AccessibilitySummarySection } from '@/components/AccessibilitySummarySection/AccessibilitySummarySection'
import { SynchronizedProviderInformation } from '@/components/SynchronisedProviderInformation/SynchronizedProviderInformation'
import { SummaryContent } from '@/ui-kit/SummaryLayout/SummaryContent'
import { SummaryDescriptionList } from '@/ui-kit/SummaryLayout/SummaryDescriptionList'
import { SummaryLayout } from '@/ui-kit/SummaryLayout/SummaryLayout'
import { SummarySection } from '@/ui-kit/SummaryLayout/SummarySection'
import { SummarySubSection } from '@/ui-kit/SummaryLayout/SummarySubSection'

import styles from './CollectiveOfferSummary.module.scss'
import { CollectiveOfferContactSection } from './components/CollectiveOfferContactSection'
import { CollectiveOfferDateSection } from './components/CollectiveOfferDateSection'
import { CollectiveOfferImagePreview } from './components/CollectiveOfferImagePreview'
import { CollectiveOfferInstitutionSection } from './components/CollectiveOfferInstitutionSection'
import { CollectiveOfferLocationSection } from './components/CollectiveOfferLocationSection'
import { CollectiveOfferNotificationSection } from './components/CollectiveOfferNotificationSection'
import { CollectiveOfferParticipantSection } from './components/CollectiveOfferParticipantSection'
import { CollectiveOfferPriceSection } from './components/CollectiveOfferPriceSection'
import { CollectiveOfferStockSection } from './components/CollectiveOfferStockSection'
import { CollectiveOfferTypeSection } from './components/CollectiveOfferTypeSection'
import { CollectiveOfferVenueSection } from './components/CollectiveOfferVenueSection'

type LayoutProps = {
  offer:
    | GetCollectiveOfferResponseModel
    | GetCollectiveOfferTemplateResponseModel
  canEditDetails: boolean
  canEditDatesAndPrice: boolean
  canEditInstitution: boolean
  offerEditLink?: string
  stockEditLink?: string
  institutionEditLink?: string
}

type NewPriceLayoutProps = Omit<LayoutProps, 'offer'> & {
  offer: GetCollectiveOfferResponseModel
}

function _renderNewPriceLayout({
  offer,
  canEditDetails,
  canEditDatesAndPrice,
  canEditInstitution,
  offerEditLink,
  stockEditLink,
  institutionEditLink,
}: NewPriceLayoutProps) {
  return (
    <>
      <SummarySection
        title="Détails de l’offre"
        editLink={canEditDetails ? offerEditLink : null}
      >
        <CollectiveOfferVenueSection venue={offer.venue} />
        <CollectiveOfferTypeSection offer={offer} />
        <CollectiveOfferImagePreview offer={offer} />
        <CollectiveOfferLocationSection offer={offer} />
        <CollectiveOfferParticipantSection students={offer.students} />
        <AccessibilitySummarySection
          accessibleItem={offer}
          accessibleWording="Votre offre est accessible aux publics en situation de handicap :"
          shouldShowDivider
        />
      </SummarySection>
      <SummarySection
        title="Dates et prix"
        editLink={canEditDatesAndPrice ? stockEditLink : null}
      >
        <CollectiveOfferStockSection
          stock={offer.collectiveStock}
          venueDepartmentCode={offer.venue.departementCode}
        />
      </SummarySection>
      <SummarySection
        title="Informations pratiques"
        editLink={canEditDetails ? offerEditLink : null}
      >
        {offer.bookingEmails.length > 0 && (
          <CollectiveOfferNotificationSection
            bookingEmails={offer.bookingEmails}
          />
        )}
        <CollectiveOfferContactSection offer={offer} />
        {offer.collectiveStock?.priceDetail && (
          <SummarySubSection title="Informations pratiques" shouldShowDivider>
            <SummaryDescriptionList
              descriptions={[{ text: offer.collectiveStock.priceDetail }]}
            />
          </SummarySubSection>
        )}
      </SummarySection>
      <SummarySection
        title="Établissement et enseignant"
        editLink={canEditInstitution ? institutionEditLink : null}
      >
        <CollectiveOfferInstitutionSection
          institution={offer.institution}
          teacher={offer.teacher}
        />
      </SummarySection>
    </>
  )
}

type OldLayoutProps = LayoutProps & {
  shouldShowAccessibilityDivider: boolean
}

function _renderOldLayout({
  offer,
  canEditDetails,
  canEditDatesAndPrice,
  canEditInstitution,
  shouldShowAccessibilityDivider,
  offerEditLink,
  stockEditLink,
  institutionEditLink,
}: OldLayoutProps) {
  return (
    <>
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
          shouldShowDivider={shouldShowAccessibilityDivider}
        />
        <CollectiveOfferContactSection offer={offer} />
        {offer.bookingEmails.length > 0 && (
          <CollectiveOfferNotificationSection
            bookingEmails={offer.bookingEmails}
          />
        )}
      </SummarySection>
      {isCollectiveOffer(offer) && (
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
      {isCollectiveOffer(offer) && (
        <SummarySection
          title="Établissement et enseignant"
          editLink={canEditInstitution ? institutionEditLink : null}
        >
          <CollectiveOfferInstitutionSection
            institution={offer.institution}
            teacher={offer.teacher}
          />
        </SummarySection>
      )}
    </>
  )
}

export interface CollectiveOfferSummaryProps {
  offer:
    | GetCollectiveOfferTemplateResponseModel
    | GetCollectiveOfferResponseModel
  offerEditLink?: string
  stockEditLink?: string
  institutionEditLink?: string
}

export const CollectiveOfferSummary = ({
  offer,
  offerEditLink,
  stockEditLink,
  institutionEditLink,
}: CollectiveOfferSummaryProps) => {
  const isNewCollectivePriceEnabled = useActiveFeature(
    'WIP_ENABLE_NEW_COLLECTIVE_PRICE_DETAILS'
  )

  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)

  const isVenueClosed = withVenueHelpers(selectedPartnerVenue).isClosed
  const canEditDetails =
    isCollectiveOfferDetailsEditable(offer) && !isVenueClosed
  const canEditDatesAndPrice =
    isCollectiveStockEditable(offer) && !isVenueClosed
  const canEditInstitution =
    isCollectiveInstitutionEditable(offer) && !isVenueClosed

  const layoutProps = {
    offer,
    canEditDetails,
    canEditDatesAndPrice,
    canEditInstitution,
    offerEditLink,
    stockEditLink,
    institutionEditLink,
  }

  return (
    <SummaryLayout>
      <SummaryContent fullWidth>
        {isCollectiveOffer(offer) && offer.provider?.name && (
          <div className={styles['banner-container']}>
            <SynchronizedProviderInformation
              providerName={offer.provider.name}
            />
          </div>
        )}
        {isNewCollectivePriceEnabled && isCollectiveOffer(offer)
          ? _renderNewPriceLayout({ ...layoutProps, offer })
          : _renderOldLayout({
              ...layoutProps,
              shouldShowAccessibilityDivider: !isNewCollectivePriceEnabled,
            })}
      </SummaryContent>
    </SummaryLayout>
  )
}
