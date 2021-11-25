import React, { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'

import Spinner from 'components/layout/Spinner'
import * as pcapi from 'repository/pcapi/pcapi'
import OfferEducationalStockScreen from 'screens/OfferEducationalStock'
import {
  Offer,
  OfferEducationalStockFormValues,
} from 'screens/OfferEducationalStock/types'

const OfferEducationalStockCreation = (): JSX.Element => {
  const [offer, setOffer] = useState<Offer | null>(null)
  const [isReady, setIsReady] = useState<boolean>(false)
  const { offerId } = useParams<{ offerId: string }>()

  const initialValues: OfferEducationalStockFormValues = {
    eventDate: new Date(),
    eventTime: '',
    numberOfPlaces: '',
    totalPrice: '',
    bookingLimitDatetime: new Date(),
  }

  useEffect(() => {
    pcapi.loadOffer(offerId).then((offer: Offer) => {
      setOffer(offer)
      setIsReady(true)
    })
  }, [offerId])

  return offer && isReady ? (
    <OfferEducationalStockScreen
      initialValues={initialValues}
      offer={offer}
      onSubmit={(values: OfferEducationalStockFormValues) =>
        console.log(values)
      }
    />
  ) : (
    <Spinner />
  )
}

export default OfferEducationalStockCreation
