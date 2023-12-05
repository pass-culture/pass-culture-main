import React from 'react'

import { AppLayout } from 'app/AppLayout'
import RouteLeavingGuardCollectiveOfferCreation from 'components/RouteLeavingGuardCollectiveOfferCreation'
import CollectiveOfferConfirmationScreen from 'screens/CollectiveOfferConfirmation'
import {
  MandatoryCollectiveOfferFromParamsProps,
  withCollectiveOfferFromParams,
} from 'screens/OfferEducational/useCollectiveOfferFromParams'

const CollectiveOfferConfirmation = ({
  offer,
}: MandatoryCollectiveOfferFromParamsProps): JSX.Element => {
  const getInstitutionDisplayName = () => {
    if (offer.isTemplate) {
      return ''
    }

    if (!offer.institution) {
      return ''
    }

    return `${offer.institution.institutionType ?? ''} ${
      offer.institution.name ?? ''
    }`.trim()
  }

  return (
    <AppLayout>
      <CollectiveOfferConfirmationScreen
        isShowcase={offer.isTemplate}
        offerStatus={offer?.status}
        offererId={offer.venue.managingOfferer.id}
        institutionDisplayName={getInstitutionDisplayName()}
      />
      <RouteLeavingGuardCollectiveOfferCreation />
    </AppLayout>
  )
}

export default withCollectiveOfferFromParams(CollectiveOfferConfirmation)
