import React from 'react'
import { useHistory } from 'react-router-dom'

import { NOTIFICATION_LONG_SHOW_DURATION } from 'core/Notification/constants'
import {
  Mode,
  OfferEducationalStockFormValues,
  cancelCollectiveBookingAdapter,
  extractInitialStockValues,
  getStockCollectiveOfferAdapter,
  patchIsCollectiveOfferActiveAdapter,
  CollectiveOffer,
} from 'core/OfferEducational'
import { computeURLCollectiveOfferId } from 'core/OfferEducational/utils/computeURLCollectiveOfferId'
import useNotification from 'hooks/useNotification'
import OfferEducationalStockScreen from 'screens/OfferEducationalStock'

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

  const initialValues = extractInitialStockValues(offer)
  const notify = useNotification()

  const handleSubmitStock = async (
    offer: CollectiveOffer,
    values: OfferEducationalStockFormValues
  ) => {
    if (!offer.collectiveStock) {
      return notify.error('Impossible de mettre à jour le stock.')
    }

    const stockResponse = await patchCollectiveStockAdapter({
      offer,
      stockId: offer.collectiveStock.id,
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

  return (
    <OfferEducationalStockScreen
      cancelActiveBookings={cancelActiveBookings}
      initialValues={initialValues}
      mode={
        offer.collectiveStock?.isEducationalStockEditable
          ? Mode.EDITION
          : Mode.READ_ONLY
      }
      offer={offer}
      onSubmit={handleSubmitStock}
      setIsOfferActive={setIsOfferActive}
    />
  )
}

export default CollectiveOfferStockEdition
