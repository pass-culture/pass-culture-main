import {
  DEFAULT_EAC_STOCK_FORM_VALUES,
  EducationalOfferType,
  GetStockOfferSuccessPayload,
  Mode,
  OfferEducationalStockFormValues,
  cancelActiveBookingsAdapter,
  extractInitialStockValues,
  extractOfferIdAndOfferTypeFromRouteParams,
  patchIsTemplateOfferActiveAdapter,
} from 'core/OfferEducational'
import React, { useEffect, useState } from 'react'
import { useHistory, useParams } from 'react-router-dom'

import { GetCollectiveOfferTemplateSuccessPayload } from './types'
import { OfferBreadcrumbStep } from 'new_components/OfferBreadcrumb'
import OfferEducationalLayout from 'new_components/OfferEducationalLayout'
import OfferEducationalStockScreen from 'screens/OfferEducationalStock'
import Spinner from 'components/layout/Spinner'
import { getCollectiveOfferTemplateAdapter } from './adapters/getCollectiveOfferTemplateAdapter'
import { patchCollectiveOfferTemplateAdapter } from './adapters/patchCollectiveOfferTemplateAdapter'
import { patchCollectiveOfferTemplateIntoCollectiveOfferAdapter } from './adapters/patchCollectiveOfferTemplateIntoCollectiveOffer'
import useNotification from 'components/hooks/useNotification'

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
  const [offer, setOffer] =
    useState<GetCollectiveOfferTemplateSuccessPayload | null>(null)
  const [isReady, setIsReady] = useState<boolean>(false)
  const { offerId: offerIdFromParams } = useParams<{ offerId: string }>()
  const { offerId } =
    extractOfferIdAndOfferTypeFromRouteParams(offerIdFromParams)
  const notify = useNotification()

  const handleSubmitStock = async (
    offer: GetStockOfferSuccessPayload,
    values: OfferEducationalStockFormValues
  ) => {
    const adapter = getAdapter(values.educationalOfferType)

    const stockResponse = await adapter({
      offer,
      values,
    })

    if (
      stockResponse.isOk &&
      values.educationalOfferType === EducationalOfferType.CLASSIC
    ) {
      return history.push(
        `/offre/${stockResponse.payload.offerId}/collectif/stocks/edition`
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
    const initialValuesFromStock = offerResponse.payload.isShowcase
      ? {
          ...DEFAULT_EAC_STOCK_FORM_VALUES,
          priceDetail: stockResponse.payload.educationalPriceDetail ?? '',
          educationalOfferType: EducationalOfferType.SHOWCASE,
        }
      : extractInitialStockValues(
          stockResponse.payload,
          offerResponse.payload,
          EducationalOfferType.CLASSIC
        )
    setInitialValues(initialValuesFromStock)
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
    const { isOk, message } = await cancelActiveBookingsAdapter({
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
          priceDetail: offerResponse.payload.educationalPriceDetails ?? '',
          educationalOfferType: EducationalOfferType.SHOWCASE,
        }
        setInitialValues(initialValuesFromStock)
        setIsReady(true)
      }
      loadStockAndOffer()
    }
  }, [offerId, isReady, notify, history])

  return (
    <OfferEducationalLayout
      activeStep={OfferBreadcrumbStep.STOCKS}
      isCreatingOffer={false}
      offerId={offerIdFromParams}
      title="Éditer une offre collective"
    >
      {offer && isReady ? (
        <OfferEducationalStockScreen
          cancelActiveBookings={cancelActiveBookings}
          initialValues={initialValues}
          mode={Mode.EDITION} // a collective offer template is always editable
          offer={offer}
          onSubmit={handleSubmitStock}
          setIsOfferActive={setIsOfferActive}
        />
      ) : (
        <Spinner />
      )}
    </OfferEducationalLayout>
  )
}

export default CollectiveOfferTemplateStockEdition
