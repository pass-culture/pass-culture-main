import React from 'react'

import PageTitle from 'components/PageTitle/PageTitle'
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
    <>
      <PageTitle title="Confirmation" />
      <CollectiveOfferConfirmationScreen
        isShowcase={offer.isTemplate}
        offerStatus={offer?.status}
        offererId={offer.venue.managingOffererId}
        institutionDisplayName={getInstitutionDisplayName()}
      />
      <RouteLeavingGuardCollectiveOfferCreation />
    </>
  )
}

export default withCollectiveOfferFromParams(CollectiveOfferConfirmation)
