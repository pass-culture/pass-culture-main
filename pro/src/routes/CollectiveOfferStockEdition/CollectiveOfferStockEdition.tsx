import React, { useEffect, useState } from 'react'
import { useHistory } from 'react-router-dom'

import { CollectiveStockResponseModel } from 'apiClient/v1'
import { NOTIFICATION_LONG_SHOW_DURATION } from 'core/Notification/constants'
import {
  DEFAULT_EAC_STOCK_FORM_VALUES,
  EducationalOfferType,
  Mode,
  OfferEducationalStockFormValues,
  cancelCollectiveBookingAdapter,
  extractInitialStockValues,
  getStockCollectiveOfferAdapter,
  patchIsCollectiveOfferActiveAdapter,
  CollectiveOffer,
} from 'core/OfferEducational'
import { getCollectiveStockAdapter } from 'core/OfferEducational/adapters/getCollectiveStockAdapter'
import { computeURLCollectiveOfferId } from 'core/OfferEducational/utils/computeURLCollectiveOfferId'
import useNotification from 'hooks/useNotification'
import OfferEducationalStockScreen from 'screens/OfferEducationalStock'
import Spinner from 'ui-kit/Spinner/Spinner'

import patchCollectiveStockAdapter from './adapters/patchCollectiveStockAdapter'

interface OfferEducationalStockEditionProps {
  offer: CollectiveOffer
  reloadCollectiveOffer: () => void
}

const CollectiveOfferStockEdition = ({
  offer,
  reloadCollectiveOffer,
}: OfferEducationalStockEditionProps): JSX.Element => {
  const history = useHistory()

  const [initialValues, setInitialValues] =
    useState<OfferEducationalStockFormValues>(DEFAULT_EAC_STOCK_FORM_VALUES)
  const [stock, setStock] = useState<CollectiveStockResponseModel | null>(null)
  const [isReady, setIsReady] = useState<boolean>(false)
  const notify = useNotification()

  const handleSubmitStock = async (
    offer: CollectiveOffer,
    values: OfferEducationalStockFormValues
  ) => {
    if (!stock) {
      return notify.error('Impossible de mettre à jour le stock.')
    }

    const stockResponse = await patchCollectiveStockAdapter({
      offer,
      stockId: stock.id,
      values,
      initialValues,
    })
    const offerResponse = await getStockCollectiveOfferAdapter(offer.id)

    if (!stockResponse.isOk) {
      return notify.error(stockResponse.message)
    }

    if (!offerResponse.isOk) {
      return notify.error(offerResponse.message)
    }

    notify.success(stockResponse.message)
    reloadCollectiveOffer()
    history.push(
      `/offre/${computeURLCollectiveOfferId(
        offer.id,
        false
      )}/collectif/recapitulatif`
    )
  }

  const setIsOfferActive = async (isActive: boolean) => {
    const { isOk, message } = await patchIsCollectiveOfferActiveAdapter({
      isActive,
      offerId: offer.id,
    })

    if (!isOk) {
      return notify.error(message)
    }

    notify.success(message)
    reloadCollectiveOffer()
  }

  const cancelActiveBookings = async () => {
    const { isOk, message } = await cancelCollectiveBookingAdapter({
      offerId: offer.id,
    })

    if (!isOk) {
      return notify.error(message, {
        duration: NOTIFICATION_LONG_SHOW_DURATION,
      })
    }

    notify.success(message, { duration: NOTIFICATION_LONG_SHOW_DURATION })
    reloadCollectiveOffer()
  }

  useEffect(() => {
    if (!isReady) {
      const loadStockAndOffer = async () => {
        const stockResponse = await getCollectiveStockAdapter({
          offerId: offer.id,
        })

        if (!stockResponse.isOk) {
          return notify.error(stockResponse.message)
        }
        setStock(stockResponse.payload.stock)
        const initialValuesFromStock = offer.isTemplate
          ? {
              ...DEFAULT_EAC_STOCK_FORM_VALUES,
              priceDetail:
                stockResponse.payload.stock?.educationalPriceDetail ?? '',
              educationalOfferType: EducationalOfferType.SHOWCASE,
            }
          : extractInitialStockValues(
              stockResponse.payload.stock,
              offer,
              offer.isTemplate
                ? EducationalOfferType.SHOWCASE
                : EducationalOfferType.CLASSIC
            )
        setInitialValues(initialValuesFromStock)
        setIsReady(true)
      }
      loadStockAndOffer()
    }
  }, [offer.id, isReady, notify, history])

  if (!isReady) {
    return <Spinner />
  }

  return (
    <OfferEducationalStockScreen
      cancelActiveBookings={cancelActiveBookings}
      initialValues={initialValues}
      mode={stock?.isEducationalStockEditable ? Mode.EDITION : Mode.READ_ONLY}
      offer={offer}
      onSubmit={handleSubmitStock}
      setIsOfferActive={setIsOfferActive}
    />
  )
}

export default CollectiveOfferStockEdition
