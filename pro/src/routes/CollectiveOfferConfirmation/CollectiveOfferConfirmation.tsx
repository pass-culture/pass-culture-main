import React, { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'

import Spinner from 'components/layout/Spinner'
import {
  GetStockOfferSuccessPayload,
  extractOfferIdAndOfferTypeFromRouteParams,
  getStockCollectiveOfferAdapter,
} from 'core/OfferEducational'
import { getStockCollectiveOfferTemplateAdapter } from 'core/OfferEducational/adapters/getStockCollectiveOfferTemplateAdapter'
import useNotification from 'hooks/useNotification'
import CollectiveOfferConfirmationScreen from 'screens/CollectiveOfferConfirmation'

const CollectiveOfferConfirmation = (): JSX.Element => {
  const { offerId: offerIdFromParams } = useParams<{ offerId: string }>()
  const { offerId, isShowcase } =
    extractOfferIdAndOfferTypeFromRouteParams(offerIdFromParams)
  const [offer, setOffer] = useState<GetStockOfferSuccessPayload>()
  const notify = useNotification()

  useEffect(() => {
    const loadOffer = async () => {
      const getOfferAdapter = isShowcase
        ? getStockCollectiveOfferTemplateAdapter
        : getStockCollectiveOfferAdapter

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

  const { institutionType, name } = offer?.institution ?? {}
  const institutionDisplayName = `${institutionType ?? ''} ${name ?? ''}`.trim()

  return (
    <CollectiveOfferConfirmationScreen
      isShowcase={offer?.isShowcase}
      offerStatus={offer?.status}
      offererId={offer?.managingOffererId}
      institutionDisplayName={institutionDisplayName}
    />
  )
}

export default CollectiveOfferConfirmation
