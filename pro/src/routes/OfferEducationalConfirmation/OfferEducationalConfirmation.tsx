import {
  GetStockOfferSuccessPayload,
  extractOfferIdAndOfferTypeFromRouteParams,
  getStockCollectiveOfferAdapter,
  getStockOfferAdapter,
} from 'core/OfferEducational'
import React, { useEffect, useState } from 'react'

import OfferEducationalConfirmationScreen from 'screens/OfferEducationalConfirmation'
import Spinner from 'components/layout/Spinner'
import { getStockCollectiveOfferTemplateAdapter } from 'core/OfferEducational/adapters/getStockCollectiveOfferTemplateAdapter'
import useActiveFeature from 'components/hooks/useActiveFeature'
import useNotification from 'components/hooks/useNotification'
import { useParams } from 'react-router-dom'

const OfferEducationalConfirmation = (): JSX.Element => {
  const { offerId: offerIdFromParams } = useParams<{ offerId: string }>() 
  const { offerId, isShowcase } =
    extractOfferIdAndOfferTypeFromRouteParams(offerIdFromParams)
  const [offer, setOffer] = useState<GetStockOfferSuccessPayload>()
  const notify = useNotification()
  const enableIndividualAndCollectiveSeparation = useActiveFeature(
    'ENABLE_INDIVIDUAL_AND_COLLECTIVE_OFFER_SEPARATION'
  )

  useEffect(() => {
    const loadOffer = async () => {
      const getOfferAdapter = enableIndividualAndCollectiveSeparation
        ? isShowcase
          ? getStockCollectiveOfferTemplateAdapter
          : getStockCollectiveOfferAdapter
        : getStockOfferAdapter

      const offerResponse = await getOfferAdapter(offerId)

      if (!offerResponse.isOk) {
        return notify.error(offerResponse.message)
      }

      setOffer(offerResponse.payload)
    }

    loadOffer()
  }, [offerId, notify])

  if (!offer) {
    return <Spinner />
  }

  return (
    <OfferEducationalConfirmationScreen
      isShowcase={offer?.isShowcase}
      offerStatus={offer?.status}
      offererId={offer?.managingOffererId}
    />
  )
}

export default OfferEducationalConfirmation
