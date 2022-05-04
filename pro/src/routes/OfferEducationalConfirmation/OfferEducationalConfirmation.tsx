import React, { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'

import useNotification from 'components/hooks/useNotification'
import Spinner from 'components/layout/Spinner'
import {
  getStockOfferAdapter,
  GetStockOfferSuccessPayload,
} from 'core/OfferEducational'
import OfferEducationalConfirmationScreen from 'screens/OfferEducationalConfirmation'

const OfferEducationalConfirmation = (): JSX.Element => {
  const { offerId } = useParams<{ offerId: string }>()
  const [offer, setOffer] = useState<GetStockOfferSuccessPayload>()
  const notify = useNotification()

  useEffect(() => {
    const loadOffer = async () => {
      const offerResponse = await getStockOfferAdapter(offerId)

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
