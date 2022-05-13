import {
  GetStockOfferSuccessPayload,
  getStockOfferAdapter,
} from 'core/OfferEducational'
import React, { useEffect, useState } from 'react'

import OfferEducationalConfirmationScreen from 'screens/OfferEducationalConfirmation'
import Spinner from 'components/layout/Spinner'
import useNotification from 'components/hooks/useNotification'
import { useParams } from 'react-router-dom'

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
