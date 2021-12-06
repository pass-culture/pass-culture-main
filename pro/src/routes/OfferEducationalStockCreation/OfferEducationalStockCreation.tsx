import React, { useState, useEffect } from 'react'
import { useHistory } from 'react-router'
import { useParams } from 'react-router-dom'

import useNotification from 'components/hooks/useNotification'
import Spinner from 'components/layout/Spinner'
import {
  Offer,
  OfferEducationalStockFormValues,
} from 'core/OfferEducationalStock/types'
import * as pcapi from 'repository/pcapi/pcapi'
import OfferEducationalStockScreen from 'screens/OfferEducationalStock'

import postEducationalStockAdapter from './adapters/postEducationalStock'

const OfferEducationalStockCreation = (): JSX.Element => {
  const [offer, setOffer] = useState<Offer | null>(null)
  const [isReady, setIsReady] = useState<boolean>(false)
  const { offerId } = useParams<{ offerId: string }>()
  const notify = useNotification()
  const history = useHistory()

  const initialValues: OfferEducationalStockFormValues = {
    eventDate: '',
    eventTime: '',
    numberOfPlaces: '',
    totalPrice: '',
    bookingLimitDatetime: '',
  }

  const handleSubmitStock = async (
    offer: Offer,
    values: OfferEducationalStockFormValues
  ) => {
    const { isOk, message } = await postEducationalStockAdapter({
      offer,
      values,
    })

    if (!isOk) {
      return notify.error(message)
    }
    history.push('/offre/scolaire/confirmation')
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
      onSubmit={handleSubmitStock}
    />
  ) : (
    <Spinner />
  )
}

export default OfferEducationalStockCreation
