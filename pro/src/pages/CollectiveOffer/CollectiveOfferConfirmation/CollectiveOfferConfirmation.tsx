import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import { isCollectiveOfferTemplate } from '@/commons/core/OfferEducational/types'
import { RouteLeavingGuardCollectiveOfferCreation } from '@/components/RouteLeavingGuardCollectiveOfferCreation/RouteLeavingGuardCollectiveOfferCreation'
import { CollectiveOfferConfirmationScreen } from '@/pages/CollectiveOffer/CollectiveOfferConfirmation/CollectiveOfferConfirmation/CollectiveOfferConfirmation'

import {
  type MandatoryCollectiveOfferFromParamsProps,
  withCollectiveOfferFromParams,
} from '../CollectiveOffer/components/OfferEducational/useCollectiveOfferFromParams'

const CollectiveOfferConfirmation = ({
  offer,
}: MandatoryCollectiveOfferFromParamsProps): JSX.Element => {
  const getInstitutionDisplayName = () => {
    if (isCollectiveOfferTemplate(offer)) {
      return ''
    }

    if (!offer.institution) {
      return ''
    }

    return `${offer.institution.institutionType ?? ''} ${
      offer.institution.name
    }`.trim()
  }

  return (
    <BasicLayout mainHeading="Votre offre a été publiée sur ADAGE">
      <CollectiveOfferConfirmationScreen
        isShowcase={offer.isTemplate}
        offerStatus={offer.displayedStatus}
        offererId={offer.venue.managingOfferer.id}
        institutionDisplayName={getInstitutionDisplayName()}
      />
      <RouteLeavingGuardCollectiveOfferCreation when={false} />
    </BasicLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = withCollectiveOfferFromParams(
  CollectiveOfferConfirmation
)
