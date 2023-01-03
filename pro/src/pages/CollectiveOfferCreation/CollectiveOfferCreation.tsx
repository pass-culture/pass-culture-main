import React from 'react'
import { useLocation } from 'react-router-dom'

import RouteLeavingGuardCollectiveOfferCreation from 'components/RouteLeavingGuardCollectiveOfferCreation'
import {
  CollectiveOffer,
  CollectiveOfferTemplate,
  Mode,
} from 'core/OfferEducational'
import canOffererCreateCollectiveOfferAdapter from 'core/OfferEducational/adapters/canOffererCreateCollectiveOfferAdapter'
import { queryParamsFromOfferer } from 'pages/Offers/utils/queryParamsFromOfferer'
import OfferEducationalScreen from 'screens/OfferEducational'
import useOfferEducationalFormData from 'screens/OfferEducational/useOfferEducationalFormData'
import Spinner from 'ui-kit/Spinner/Spinner'

interface CollectiveOfferCreationProps {
  offer?: CollectiveOffer | CollectiveOfferTemplate
  setOffer: (offer: CollectiveOffer | CollectiveOfferTemplate) => void
  isTemplate?: boolean
}

const CollectiveOfferCreation = ({
  offer,
  setOffer,
  isTemplate = false,
}: CollectiveOfferCreationProps): JSX.Element => {
  const location = useLocation()
  const { structure: offererId } = queryParamsFromOfferer(location)
  const { isReady, ...offerEducationalFormData } = useOfferEducationalFormData(
    offererId,
    offer
  )

  if (!isReady) {
    return <Spinner />
  }

  return (
    <>
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
    </>
  )
}

export default CollectiveOfferCreation
