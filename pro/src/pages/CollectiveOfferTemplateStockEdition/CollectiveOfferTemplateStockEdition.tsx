import React from 'react'
import { useHistory } from 'react-router-dom'

import {
  DEFAULT_EAC_STOCK_FORM_VALUES,
  EducationalOfferType,
  Mode,
  OfferEducationalStockFormValues,
  cancelCollectiveBookingAdapter,
  patchIsTemplateOfferActiveAdapter,
  CollectiveOfferTemplate,
} from 'core/OfferEducational'
import { computeURLCollectiveOfferId } from 'core/OfferEducational/utils/computeURLCollectiveOfferId'
import useNotification from 'hooks/useNotification'
import OfferEducationalStockScreen from 'screens/OfferEducationalStock'

import { patchCollectiveOfferTemplateAdapter } from './adapters/patchCollectiveOfferTemplateAdapter'

interface CollectiveOfferTemplateStockEditionProps {
  offer: CollectiveOfferTemplate
  reloadCollectiveOffer: () => void
}

const CollectiveOfferTemplateStockEdition = ({
  offer,
  reloadCollectiveOffer,
}: CollectiveOfferTemplateStockEditionProps): JSX.Element => {
  const history = useHistory()
  const notify = useNotification()

  const handleSubmitStock = async (
    offer: CollectiveOfferTemplate,
    values: OfferEducationalStockFormValues
  ) => {
    const stockResponse = await patchCollectiveOfferTemplateAdapter({
      offerId: offer.id,
      values,
    })

    if (!stockResponse.isOk) {
      return notify.error(stockResponse.message)
    }

    notify.success(stockResponse.message)
    reloadCollectiveOffer()
    history.push(
      `/offre/${computeURLCollectiveOfferId(
        offer.id,
        true
      )}/collectif/recapitulatif`
    )
  }

  const setIsOfferActive = async (isActive: boolean) => {
    const { isOk, message } = await patchIsTemplateOfferActiveAdapter({
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
      return notify.error(message)
    }

    notify.success(message)
    reloadCollectiveOffer()
  }

  return (
    <OfferEducationalStockScreen
      cancelActiveBookings={cancelActiveBookings}
      initialValues={{
        ...DEFAULT_EAC_STOCK_FORM_VALUES,
        priceDetail: offer.educationalPriceDetail ?? '',
        educationalOfferType: EducationalOfferType.SHOWCASE,
      }}
      mode={Mode.EDITION} // a collective offer template is always editable
      offer={offer}
      onSubmit={handleSubmitStock}
      setIsOfferActive={setIsOfferActive}
    />
  )
}

export default CollectiveOfferTemplateStockEdition
