import React, { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'

import useNotification from 'components/hooks/useNotification'
import Spinner from 'components/layout/Spinner'
import { getOfferAdapter, Mode } from 'core/OfferEducational'
import { DEFAULT_EAC_STOCK_FORM_VALUES } from 'core/OfferEducationalStock/constants'
import { OfferEducationalStockFormValues } from 'core/OfferEducationalStock/types'
import { Offer } from 'custom_types/offer'
import OfferEducationalStockScreen from 'screens/OfferEducationalStock'

import { getEducationalStockAdapter } from './adapters/getEducationalStockAdapter'
import patchEducationalStockAdapter from './adapters/patchEducationalStock'
import { extractInitialStockValues } from './extractInitialStockValues'
import { StockResponse } from './types'

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
    const stockId = stock?.id
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
        const results = await Promise.all([
          getOfferAdapter(offerId),
          getEducationalStockAdapter(offerId),
        ])
        if (results.some(res => !res.isOk)) {
          return notify.error(results?.find(res => !res.isOk)?.message)
        }
        const [offerResponse, stockResponse] = results
        setOffer(offerResponse.payload.offer)
        setStock(stockResponse.payload.stock)
        const initialValuesFromStock = extractInitialStockValues(
          stockResponse.payload.stock,
          offerResponse.payload.offer
        )
        setInitialValues(initialValuesFromStock)
        setIsReady(true)
        return
      }
      loadStockAndOffer()
    }
  }, [offerId, isReady, notify])

  return offer && isReady ? (
    <OfferEducationalStockScreen
      initialValues={initialValues}
      isEditable={stock?.isStockEditable}
      mode={Mode.EDITION}
      offer={offer}
      onSubmit={handleSubmitStock}
    />
  ) : (
    <Spinner />
  )
}

export default OfferEducationalStockEdition
