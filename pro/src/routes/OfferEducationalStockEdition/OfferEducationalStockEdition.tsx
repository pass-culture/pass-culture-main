import React, { useEffect, useState } from 'react'
import { useHistory, useParams } from 'react-router-dom'

import { CollectiveStockResponseModel } from 'apiClient/v1'
import useNotification from 'components/hooks/useNotification'
import Spinner from 'components/layout/Spinner'
import {
  DEFAULT_EAC_STOCK_FORM_VALUES,
  EducationalOfferType,
  GetStockOfferSuccessPayload,
  Mode,
  OfferEducationalStockFormValues,
  cancelCollectiveBookingAdapter,
  extractInitialStockValues,
  getStockCollectiveOfferAdapter,
  patchIsCollectiveOfferActiveAdapter,
} from 'core/OfferEducational'
import { getCollectiveStockAdapter } from 'core/OfferEducational/adapters/getCollectiveStockAdapter'
import { OfferBreadcrumbStep } from 'new_components/OfferBreadcrumb'
import OfferEducationalLayout from 'new_components/OfferEducationalLayout'
import OfferEducationalStockScreen from 'screens/OfferEducationalStock'

import patchCollectiveStockAdapter from './adapters/patchCollectiveStockAdapter'

const OfferEducationalStockEdition = (): JSX.Element => {
  const history = useHistory()

  const [initialValues, setInitialValues] =
    useState<OfferEducationalStockFormValues>(DEFAULT_EAC_STOCK_FORM_VALUES)
  const [offer, setOffer] = useState<GetStockOfferSuccessPayload | null>(null)
  const [stock, setStock] = useState<CollectiveStockResponseModel | null>(null)
  const [isReady, setIsReady] = useState<boolean>(false)
  const { offerId } = useParams<{ offerId: string }>()
  const notify = useNotification()

  const handleSubmitStock = async (
    offer: GetStockOfferSuccessPayload,
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
    const offerResponse = await getStockCollectiveOfferAdapter(offerId)
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
          values.educationalOfferType
        )
    setInitialValues(initialValuesFromStock)
  }

  const setIsOfferActive = async (isActive: boolean) => {
    const patchOfferId = offerId

    const { isOk, message } = await patchIsCollectiveOfferActiveAdapter({
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
    const patchOfferId = offerId
    const { isOk, message } = await cancelCollectiveBookingAdapter({
      offerId: patchOfferId,
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
        const [offerResponse, stockResponse] = await Promise.all([
          getStockCollectiveOfferAdapter(offerId),
          getCollectiveStockAdapter({
            offerId,
          }),
        ])
        if (!offerResponse.isOk) {
          return notify.error(offerResponse.message)
        }

        if (!offerResponse.payload.isEducational) {
          return history.push(`/offre/${offerId}/individuel/stocks`)
        }

        if (!stockResponse.isOk) {
          return notify.error(stockResponse.message)
        }
        setOffer(offerResponse.payload)
        setStock(stockResponse.payload.stock)
        const initialValuesFromStock = offerResponse.payload.isShowcase
          ? {
              ...DEFAULT_EAC_STOCK_FORM_VALUES,
              priceDetail:
                stockResponse.payload.stock?.educationalPriceDetail ?? '',
              educationalOfferType: EducationalOfferType.SHOWCASE,
            }
          : extractInitialStockValues(
              stockResponse.payload.stock,
              offerResponse.payload,
              offerResponse.payload.isShowcase
                ? EducationalOfferType.SHOWCASE
                : EducationalOfferType.CLASSIC
            )
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
      offerId={offerId}
      title="Éditer une offre collective"
    >
      {offer && isReady ? (
        <OfferEducationalStockScreen
          cancelActiveBookings={cancelActiveBookings}
          initialValues={initialValues}
          mode={
            stock?.isEducationalStockEditable ? Mode.EDITION : Mode.READ_ONLY
          }
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

export default OfferEducationalStockEdition
