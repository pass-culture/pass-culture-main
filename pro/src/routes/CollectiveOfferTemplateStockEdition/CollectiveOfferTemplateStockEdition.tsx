import React, { useEffect, useState } from 'react'
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
import { patchCollectiveOfferTemplateIntoCollectiveOfferAdapter } from './adapters/patchCollectiveOfferTemplateIntoCollectiveOffer'

const getAdapter = (educationalOfferType: EducationalOfferType) => {
  if (educationalOfferType === EducationalOfferType.CLASSIC) {
    return patchCollectiveOfferTemplateIntoCollectiveOfferAdapter
  }

  return patchCollectiveOfferTemplateAdapter
}

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

  const [initialValues, setInitialValues] =
    useState<OfferEducationalStockFormValues>(DEFAULT_EAC_STOCK_FORM_VALUES)

  const handleSubmitStock = async (
    offer: CollectiveOfferTemplate,
    values: OfferEducationalStockFormValues
  ) => {
    const adapter = getAdapter(values.educationalOfferType)

    const stockResponse = await adapter({
      offerId: offer.id,
      values,
      departmentCode: offer.venue.departementCode ?? '',
    })

    if (
      stockResponse.isOk &&
      values.educationalOfferType === EducationalOfferType.CLASSIC
    ) {
      return history.push(
        `/offre/${stockResponse.payload.offerId}/collectif/visibilite/edition`
      )
    }

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

  useEffect(() => {
    const initialValuesFromStock = {
      ...DEFAULT_EAC_STOCK_FORM_VALUES,
      priceDetail: offer.educationalPriceDetail ?? '',
      educationalOfferType: EducationalOfferType.SHOWCASE,
    }
    setInitialValues(initialValuesFromStock)
  }, [])

  return (
    <OfferEducationalStockScreen
      cancelActiveBookings={cancelActiveBookings}
      initialValues={initialValues}
      mode={Mode.EDITION} // a collective offer template is always editable
      offer={offer}
      onSubmit={handleSubmitStock}
      setIsOfferActive={setIsOfferActive}
    />
  )
}

export default CollectiveOfferTemplateStockEdition
