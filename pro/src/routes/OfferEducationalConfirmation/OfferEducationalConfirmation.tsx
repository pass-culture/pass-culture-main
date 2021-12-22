import React, { useEffect, useState } from 'react'
import { useLocation, useParams } from 'react-router'

import useNotification from 'components/hooks/useNotification'
import Spinner from 'components/layout/Spinner'
import { queryParamsFromOfferer } from 'components/pages/Offers/utils/queryParamsFromOfferer'
import { getStockOfferAdapter } from 'core/OfferEducational'
import { OfferStatus } from 'custom_types/offer'
import OfferEducationalConfirmationScreen from 'screens/OfferEducationalConfirmation'

const OfferEducationalConfirmation = (): JSX.Element => {
  const location = useLocation<{ structure?: string; lieu?: string }>()
  const { offerId } = useParams<{ offerId: string }>()
  const [offerStatus, setOfferStatus] = useState<undefined | OfferStatus>()
  const notify = useNotification()

  const { structure: offererId, lieu: venueId } =
    queryParamsFromOfferer(location)

  useEffect(() => {
    const loadOffer = async () => {
      const offerResponse = await getStockOfferAdapter(offerId)

      if (!offerResponse.isOk) {
        return notify.error(offerResponse.message)
      }

      setOfferStatus(offerResponse.payload.status)
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
      venueId={venueId}
    />
  )
}

export default OfferEducationalConfirmation
