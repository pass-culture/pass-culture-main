import React from 'react'

import { CollectiveOffer, CollectiveOfferTemplate } from 'core/OfferEducational'
import RouteLeavingGuardOfferCreation from 'new_components/RouteLeavingGuardOfferCreation'
import CollectiveOfferConfirmationScreen from 'screens/CollectiveOfferConfirmation'

interface CollectiveOfferConfirmationProps {
  offer: CollectiveOffer | CollectiveOfferTemplate
}

const CollectiveOfferConfirmation = ({
  offer,
}: CollectiveOfferConfirmationProps): JSX.Element => {
  const getInstitutionDisplayName = () => {
    if (offer.isTemplate) return ''

    if (!offer.institution) return ''

    return `${offer.institution.institutionType ?? ''} ${
      offer.institution.name ?? ''
    }`.trim()
  }

  return (
    <>
      <CollectiveOfferConfirmationScreen
        isShowcase={offer.isTemplate}
        offerStatus={offer?.status}
        offererId={offer.venue.managingOffererId}
        institutionDisplayName={getInstitutionDisplayName()}
      />
      <RouteLeavingGuardOfferCreation />
    </>
  )
}

export default CollectiveOfferConfirmation
