
import { Layout } from 'app/App/layout/Layout'
import { isCollectiveOfferTemplate } from 'commons/core/OfferEducational/types'
import { RouteLeavingGuardCollectiveOfferCreation } from 'components/RouteLeavingGuardCollectiveOfferCreation/RouteLeavingGuardCollectiveOfferCreation'
import { CollectiveOfferConfirmationScreen } from 'pages/CollectiveOffer/CollectiveOfferConfirmation/CollectiveOfferConfirmation/CollectiveOfferConfirmation'

import {
  MandatoryCollectiveOfferFromParamsProps,
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
    <Layout>
      <CollectiveOfferConfirmationScreen
        isShowcase={offer.isTemplate}
        offerStatus={offer.status}
        offererId={offer.venue.managingOfferer.id}
        institutionDisplayName={getInstitutionDisplayName()}
      />
      <RouteLeavingGuardCollectiveOfferCreation when={false} />
    </Layout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = withCollectiveOfferFromParams(
  CollectiveOfferConfirmation
)
