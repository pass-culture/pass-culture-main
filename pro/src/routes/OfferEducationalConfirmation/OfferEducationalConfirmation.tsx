import React, { useEffect, useState } from 'react'
import { useParams } from 'react-router'

import useNotification from 'components/hooks/useNotification'
import Spinner from 'components/layout/Spinner'
import { getStockOfferAdapter } from 'core/OfferEducational'
import { OfferStatus } from 'custom_types/offer'
import OfferEducationalConfirmationScreen from 'screens/OfferEducationalConfirmation'

const OfferEducationalConfirmation = (): JSX.Element => {
  const { offerId } = useParams<{ offerId: string }>()
  const [offerStatus, setOfferStatus] = useState<undefined | OfferStatus>()
  const [offererId, setOffererId] = useState<string>()
  const notify = useNotification()

  useEffect(() => {
    const loadOffer = async () => {
      const offerResponse = await getStockOfferAdapter(offerId)

      if (!offerResponse.isOk) {
        return notify.error(offerResponse.message)
      }

      setOfferStatus(offerResponse.payload.status)
      setOffererId(offerResponse.payload.managingOffererId)
    }

    loadOffer()
  }, [offerId, notify])

  if (!offerStatus) {
    return <Spinner />
  }

  return (
    <OfferEducationalConfirmationScreen
      offerStatus={offerStatus}
      offererId={offererId}
    />
  )
}

export default OfferEducationalConfirmation
