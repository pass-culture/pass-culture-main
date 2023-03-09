import React from 'react'
import { useNavigate } from 'react-router-dom-v5-compat'

import CollectiveOfferLayout from 'components/CollectiveOfferLayout'
import PageTitle from 'components/PageTitle/PageTitle'
import { NOTIFICATION_LONG_SHOW_DURATION } from 'core/Notification/constants'
import {
  Mode,
  OfferEducationalStockFormValues,
  cancelCollectiveBookingAdapter,
  extractInitialStockValues,
  getStockCollectiveOfferAdapter,
  patchIsCollectiveOfferActiveAdapter,
  CollectiveOffer,
  isCollectiveOfferTemplate,
} from 'core/OfferEducational'
import { computeURLCollectiveOfferId } from 'core/OfferEducational/utils/computeURLCollectiveOfferId'
import useNotification from 'hooks/useNotification'
import {
  MandatoryCollectiveOfferFromParamsProps,
  withCollectiveOfferFromParams,
} from 'screens/OfferEducational/useCollectiveOfferFromParams'
import OfferEducationalStockScreen from 'screens/OfferEducationalStock'

import patchCollectiveStockAdapter from './adapters/patchCollectiveStockAdapter'

const CollectiveOfferStockEdition = ({
  offer,
  reloadCollectiveOffer,
  isTemplate,
}: MandatoryCollectiveOfferFromParamsProps): JSX.Element => {
  const notify = useNotification()
  const navigate = useNavigate()

  if (isCollectiveOfferTemplate(offer)) {
    throw new Error("Impossible de mettre à jour le stock d'une offre vitrine.")
  }

  const initialValues = extractInitialStockValues(offer)

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
    navigate(
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
    <CollectiveOfferLayout subTitle={offer.name} isTemplate={isTemplate}>
      <PageTitle title="Date et prix" />
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
    </CollectiveOfferLayout>
  )
}

export default withCollectiveOfferFromParams(CollectiveOfferStockEdition)
