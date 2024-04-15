import React, { useEffect, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

import { api } from 'apiClient/api'
import { isErrorAPIError } from 'apiClient/helpers'
import {
  CollectiveStockResponseModel,
  GetCollectiveOfferRequestResponseModel,
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
} from 'apiClient/v1'
import { AppLayout } from 'app/AppLayout'
import CollectiveOfferLayout from 'components/CollectiveOfferLayout'
import RouteLeavingGuardCollectiveOfferCreation from 'components/RouteLeavingGuardCollectiveOfferCreation'
import {
  createPatchStockDataPayload,
  EducationalOfferType,
  extractInitialStockValues,
  isCollectiveOffer,
  isCollectiveOfferTemplate,
  Mode,
  OfferEducationalStockFormValues,
} from 'core/OfferEducational'
import getCollectiveOfferTemplateAdapter from 'core/OfferEducational/adapters/getCollectiveOfferTemplateAdapter'
import { computeURLCollectiveOfferId } from 'core/OfferEducational/utils/computeURLCollectiveOfferId'
import { FORM_ERROR_MESSAGE } from 'core/shared'
import useNotification from 'hooks/useNotification'
import getOfferRequestInformationsAdapter from 'pages/CollectiveOfferFromRequest/adapters/getOfferRequestInformationsAdapter'
import { queryParamsFromOfferer } from 'pages/Offers/utils/queryParamsFromOfferer'
import {
  MandatoryCollectiveOfferFromParamsProps,
  withCollectiveOfferFromParams,
} from 'screens/OfferEducational/useCollectiveOfferFromParams'
import OfferEducationalStockScreen from 'screens/OfferEducationalStock'

import postCollectiveOfferTemplateAdapter from './adapters/postCollectiveOfferTemplate'
import postCollectiveStockAdapter from './adapters/postCollectiveStock'

export const CollectiveOfferStockCreation = ({
  offer,
  setOffer,
  isTemplate,
}: MandatoryCollectiveOfferFromParamsProps): JSX.Element | null => {
  const notify = useNotification()
  const navigate = useNavigate()
  const location = useLocation()
  const isCreation = !location.pathname.includes('edition')
  const { requete: requestId } = queryParamsFromOfferer(location)

  const [offerTemplate, setOfferTemplate] =
    useState<GetCollectiveOfferTemplateResponseModel>()
  const [requestInformations, setRequestInformations] =
    useState<GetCollectiveOfferRequestResponseModel | null>(null)

  const getOfferRequestInformation = async () => {
    if (requestId) {
      const { isOk, message, payload } =
        await getOfferRequestInformationsAdapter(Number(requestId))

      if (!isOk) {
        return notify.error(message)
      }
      setRequestInformations(payload)
    }
  }

  useEffect(() => {
    const fetchOfferTemplateDetails = async () => {
      if (!(isCollectiveOffer(offer) && offer.templateId)) {
        return null
      }
      const { isOk, payload, message } =
        await getCollectiveOfferTemplateAdapter(offer.templateId)
      if (!isOk) {
        return notify.error(message)
      }
      setOfferTemplate(payload)
    }

    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    fetchOfferTemplateDetails()
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    getOfferRequestInformation()
  }, [])

  if (isCollectiveOfferTemplate(offer)) {
    throw new Error(
      'Impossible de mettre à jour les stocks d’une offre vitrine.'
    )
  }

  const initialValues = extractInitialStockValues(
    offer,
    offerTemplate,
    requestInformations
  )

  /* istanbul ignore next: DEBT, TO FIX unit test submit mock */
  const handleSubmitStock = async (
    offer: GetCollectiveOfferResponseModel,
    values: OfferEducationalStockFormValues
  ) => {
    let isOk: boolean
    let message: string | null
    let createdOfferTemplateId: number | null = null
    const isTemplate =
      values.educationalOfferType === EducationalOfferType.SHOWCASE
    if (isTemplate) {
      const response = await postCollectiveOfferTemplateAdapter({
        offerId: offer.id,
        values,
      })
      isOk = response.isOk
      message = response.message
      if (!isOk) {
        return notify.error(message)
      }
      createdOfferTemplateId = response.payload ? response.payload.id : null
    } else {
      let payload: CollectiveStockResponseModel | null = null
      if (offer.collectiveStock) {
        const stockPayload = createPatchStockDataPayload(
          values,
          offer.venue.departementCode ?? '',
          initialValues
        )
        try {
          payload = await api.editCollectiveStock(
            offer.collectiveStock.id,
            stockPayload
          )
        } catch (error) {
          if (isErrorAPIError(error) && error.status === 400) {
            notify.error(FORM_ERROR_MESSAGE)
          } else {
            notify.error(
              'Une erreur est survenue lors de la mise à jour de votre stock.'
            )
          }
        }
      } else {
        const response = await postCollectiveStockAdapter({
          offer,
          values,
        })
        if (!response.isOk) {
          return notify.error(response.message)
        }
        payload = response.payload
      }
      if (payload !== null) {
        setOffer({
          ...offer,
          collectiveStock: {
            ...offer.collectiveStock,
            ...payload,
            isBooked: false,
            isCancellable: offer.isCancellable,
          },
        })
      }
    }

    let url = `/offre/${computeURLCollectiveOfferId(
      isTemplate && createdOfferTemplateId !== null
        ? createdOfferTemplateId
        : offer.id,
      isTemplate
    )}/collectif`

    if (!isTemplate) {
      url = `${url}/visibilite${requestId ? `?requete=${requestId}` : ''}`
    } else {
      url = `${url}/creation/recapitulatif`
    }
    navigate(url)
  }

  return (
    <AppLayout layout={'sticky-actions'}>
      <CollectiveOfferLayout
        subTitle={offer.name}
        isFromTemplate={isCollectiveOffer(offer) && Boolean(offer.templateId)}
        isTemplate={isTemplate}
        isCreation={isCreation}
        requestId={requestId}
      >
        <OfferEducationalStockScreen
          initialValues={initialValues}
          mode={Mode.CREATION}
          offer={offer}
          onSubmit={handleSubmitStock}
          requestId={requestId}
        />
        <RouteLeavingGuardCollectiveOfferCreation />
      </CollectiveOfferLayout>
    </AppLayout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = withCollectiveOfferFromParams(
  CollectiveOfferStockCreation
)
