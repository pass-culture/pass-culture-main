import type {
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
} from '@/apiClient/v1'
import {
  isCollectiveOffer,
  isCollectiveOfferTemplate,
} from '@/commons/core/OfferEducational/types'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import {
  isCollectiveInstitutionEditable,
  isCollectiveOfferDetailsEditable,
  isCollectiveStockEditable,
} from '@/commons/utils/isActionAllowedOnCollectiveOffer'
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

  const isOfferTemplate = isCollectiveOfferTemplate(offer)

  const canEditDetails = isCollectiveOfferDetailsEditable(offer)

  const canEditDatesAndPrice = isCollectiveStockEditable(offer)

  const canEditInstitution = isCollectiveInstitutionEditable(offer)

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
        {isNewCollectivePriceEnabled && !isOfferTemplate ? (
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
                <SummarySubSection
                  title="Informations pratiques"
                  shouldShowDivider
                >
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
        ) : (
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
                shouldShowDivider={!isNewCollectivePriceEnabled}
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
                editLink={canEditInstitution ? institutionEditLink : null}
              >
                <CollectiveOfferInstitutionSection
                  institution={offer.institution}
                  teacher={offer.teacher}
                />
              </SummarySection>
            )}
          </>
        )}
      </SummaryContent>
    </SummaryLayout>
  )
}
