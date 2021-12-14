import React, { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'

import useNotification from 'components/hooks/useNotification'
import Spinner from 'components/layout/Spinner'
import {
  DEFAULT_EAC_STOCK_FORM_VALUES,
  getOfferAdapter,
  Mode,
  OfferEducationalStockFormValues,
} from 'core/OfferEducational'
import { Offer } from 'custom_types/offer'
import OfferEducationalStockScreen from 'screens/OfferEducationalStock'

import { getEducationalStockAdapter } from './adapters/getEducationalStockAdapter'
import patchEducationalStockAdapter from './adapters/patchEducationalStockAdatper'
import { StockResponse } from './types'
import { extractInitialStockValues } from './utils/extractInitialStockValues'

const OfferEducationalStockEdition = (): JSX.Element => {
  const [initialValues, setInitialValues] =
    useState<OfferEducationalStockFormValues>(DEFAULT_EAC_STOCK_FORM_VALUES)
  const [offer, setOffer] = useState<Offer | null>(null)
  const [stock, setStock] = useState<StockResponse | null>(null)
  const [isReady, setIsReady] = useState<boolean>(false)
  const { offerId } = useParams<{ offerId: string }>()
  const notify = useNotification()

  const handleSubmitStock = async (
    offer: Offer,
    values: OfferEducationalStockFormValues
  ) => {
    if (!stock) {
      return notify.error('Impossible de mettre à jour le stock.')
    }
    const stockId = stock.id
    const { isOk, message } = await patchEducationalStockAdapter({
      offer,
      stockId,
      values,
    })

    if (!isOk) {
      return notify.error(message)
    }
    notify.success(message)
  }

  useEffect(() => {
    if (!isReady) {
      const loadStockAndOffer = async () => {
        const [offerResponse, stockResponse] = await Promise.all([
          getOfferAdapter(offerId),
          getEducationalStockAdapter(offerId),
        ])
        if (!offerResponse.isOk) {
          return notify.error(offerResponse.message)
        }
        if (!stockResponse.isOk) {
          return notify.error(stockResponse.message)
        }
        setOffer(offerResponse.payload.offer)
        setStock(stockResponse.payload.stock)
        const initialValuesFromStock = extractInitialStockValues(
          stockResponse.payload.stock,
          offerResponse.payload.offer
        )
        setInitialValues(initialValuesFromStock)
        setIsReady(true)
      }
      loadStockAndOffer()
    }
  }, [offerId, isReady, notify])

  return offer && isReady ? (
    <OfferEducationalStockScreen
      initialValues={initialValues}
      mode={stock?.isEducationalStockEditable ? Mode.EDITION : Mode.READ_ONLY}
      offer={offer}
      onSubmit={handleSubmitStock}
    />
  ) : (
    <Spinner />
  )
}

export default OfferEducationalStockEdition
