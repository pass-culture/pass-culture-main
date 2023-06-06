import React from 'react'
import { useLocation } from 'react-router-dom'

import CollectiveOfferLayout from 'components/CollectiveOfferLayout'
import RouteLeavingGuardCollectiveOfferCreation from 'components/RouteLeavingGuardCollectiveOfferCreation'
import { Mode, isCollectiveOffer } from 'core/OfferEducational'
import canOffererCreateCollectiveOfferAdapter from 'core/OfferEducational/adapters/canOffererCreateCollectiveOfferAdapter'
import { queryParamsFromOfferer } from 'pages/Offers/utils/queryParamsFromOfferer'
import OfferEducationalScreen from 'screens/OfferEducational'
import {
  OptionalCollectiveOfferFromParamsProps,
  withOptionalCollectiveOfferFromParams,
} from 'screens/OfferEducational/useCollectiveOfferFromParams'
import useOfferEducationalFormData from 'screens/OfferEducational/useOfferEducationalFormData'
import Spinner from 'ui-kit/Spinner/Spinner'

export const CollectiveOfferCreation = ({
  offer,
  setOffer,
  isTemplate,
}: OptionalCollectiveOfferFromParamsProps): JSX.Element => {
  const location = useLocation()
  const { structure: offererId, requete: requestId } =
    queryParamsFromOfferer(location)
  const { isReady, ...offerEducationalFormData } = useOfferEducationalFormData(
    offererId,
    offer
  )

  if (!isReady) {
    return <Spinner />
  }
  return (
    <CollectiveOfferLayout
      subTitle={offer?.name}
      isCreation
      isTemplate={isTemplate}
      isFromTemplate={isCollectiveOffer(offer) && Boolean(offer.templateId)}
      requestId={requestId}
    >
      <OfferEducationalScreen
        categories={offerEducationalFormData.categories}
        userOfferers={offerEducationalFormData.offerers}
        domainsOptions={offerEducationalFormData.domains}
        offer={offer}
        setOffer={setOffer}
        getIsOffererEligible={canOffererCreateCollectiveOfferAdapter}
        mode={Mode.CREATION}
        isTemplate={isTemplate}
      />
      <RouteLeavingGuardCollectiveOfferCreation />
    </CollectiveOfferLayout>
  )
}

export default withOptionalCollectiveOfferFromParams(CollectiveOfferCreation)
