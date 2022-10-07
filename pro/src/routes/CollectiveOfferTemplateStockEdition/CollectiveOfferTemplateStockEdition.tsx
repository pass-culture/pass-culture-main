import React, { useEffect, useState } from 'react'
import { useHistory, useParams } from 'react-router-dom'

import useNotification from 'components/hooks/useNotification'
import Spinner from 'components/layout/Spinner'
import {
  DEFAULT_EAC_STOCK_FORM_VALUES,
  EducationalOfferType,
  Mode,
  OfferEducationalStockFormValues,
  cancelCollectiveBookingAdapter,
  extractOfferIdAndOfferTypeFromRouteParams,
  patchIsTemplateOfferActiveAdapter,
  CollectiveOfferTemplate,
} from 'core/OfferEducational'
import getCollectiveOfferTemplateAdapter from 'core/OfferEducational/adapters/getCollectiveOfferTemplateAdapter'
import { computeURLCollectiveOfferId } from 'core/OfferEducational/utils/computeURLCollectiveOfferId'
import CollectiveOfferLayout from 'new_components/CollectiveOfferLayout'
import { OfferBreadcrumbStep } from 'new_components/OfferBreadcrumb'
import OfferEducationalStockScreen from 'screens/OfferEducationalStock'

import { patchCollectiveOfferTemplateAdapter } from './adapters/patchCollectiveOfferTemplateAdapter'
import { patchCollectiveOfferTemplateIntoCollectiveOfferAdapter } from './adapters/patchCollectiveOfferTemplateIntoCollectiveOffer'

const getAdapter = (educationalOfferType: EducationalOfferType) => {
  if (educationalOfferType === EducationalOfferType.CLASSIC) {
    return patchCollectiveOfferTemplateIntoCollectiveOfferAdapter
  }

  return patchCollectiveOfferTemplateAdapter
}

const CollectiveOfferTemplateStockEdition = (): JSX.Element => {
  const history = useHistory()

  const [initialValues, setInitialValues] =
    useState<OfferEducationalStockFormValues>(DEFAULT_EAC_STOCK_FORM_VALUES)
  const [offer, setOffer] = useState<CollectiveOfferTemplate | null>(null)
  const [isReady, setIsReady] = useState<boolean>(false)
  const { offerId: offerIdFromParams } = useParams<{ offerId: string }>()
  const { offerId } =
    extractOfferIdAndOfferTypeFromRouteParams(offerIdFromParams)
  const notify = useNotification()

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
    const offerResponse = await getCollectiveOfferTemplateAdapter(offerId)
    setOffer(offerResponse.payload)

    if (!stockResponse.isOk) {
      return notify.error(stockResponse.message)
    }

    if (!offerResponse.isOk) {
      return notify.error(offerResponse.message)
    }

    notify.success(stockResponse.message)
    history.push(
      `/offre/${computeURLCollectiveOfferId(
        offer.id,
        true
      )}/collectif/recapitulatif`
    )
  }

  const setIsOfferActive = async (isActive: boolean) => {
    const patchOfferId = offerId

    const { isOk, message } = await patchIsTemplateOfferActiveAdapter({
      isActive,
      offerId: patchOfferId,
    })

    if (!isOk) {
      return notify.error(message)
    }

    notify.success(message)
    setIsReady(false)
  }

  const cancelActiveBookings = async () => {
    const { isOk, message } = await cancelCollectiveBookingAdapter({
      offerId: offer?.offerId || '',
    })

    if (!isOk) {
      return notify.error(message)
    }

    notify.success(message)
    setIsReady(false)
  }

  useEffect(() => {
    if (!isReady) {
      const loadStockAndOffer = async () => {
        const offerResponse = await getCollectiveOfferTemplateAdapter(offerId)

        if (!offerResponse.isOk) {
          return notify.error(offerResponse.message)
        }

        setOffer(offerResponse.payload)
        const initialValuesFromStock = {
          ...DEFAULT_EAC_STOCK_FORM_VALUES,
          priceDetail: offerResponse.payload.educationalPriceDetail ?? '',
          educationalOfferType: EducationalOfferType.SHOWCASE,
        }
        setInitialValues(initialValuesFromStock)
        setIsReady(true)
      }
      loadStockAndOffer()
    }
  }, [offerId, isReady, notify, history])

  if (!offer || !isReady) {
    return <Spinner />
  }

  return (
    <CollectiveOfferLayout
      breadCrumpProps={{
        activeStep: OfferBreadcrumbStep.STOCKS,
        isCreatingOffer: false,
        offerId: offerIdFromParams,
      }}
      title="Éditer une offre collective"
      subTitle={offer.name}
    >
      <OfferEducationalStockScreen
        cancelActiveBookings={cancelActiveBookings}
        initialValues={initialValues}
        mode={Mode.EDITION} // a collective offer template is always editable
        offer={offer}
        onSubmit={handleSubmitStock}
        setIsOfferActive={setIsOfferActive}
      />
    </CollectiveOfferLayout>
  )
}

export default CollectiveOfferTemplateStockEdition
