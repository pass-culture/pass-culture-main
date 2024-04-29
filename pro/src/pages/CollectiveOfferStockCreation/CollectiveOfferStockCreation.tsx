import { useEffect, useState } from 'react'
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
import { CollectiveOfferLayout } from 'components/CollectiveOfferLayout/CollectiveOfferLayout'
import { RouteLeavingGuardCollectiveOfferCreation } from 'components/RouteLeavingGuardCollectiveOfferCreation/RouteLeavingGuardCollectiveOfferCreation'
import { getCollectiveOfferTemplateAdapter } from 'core/OfferEducational/adapters/getCollectiveOfferTemplateAdapter'
import {
  isCollectiveOffer,
  isCollectiveOfferTemplate,
  OfferEducationalStockFormValues,
  EducationalOfferType,
  Mode,
} from 'core/OfferEducational/types'
import { computeURLCollectiveOfferId } from 'core/OfferEducational/utils/computeURLCollectiveOfferId'
import { createPatchStockDataPayload } from 'core/OfferEducational/utils/createPatchStockDataPayload'
import { createStockDataPayload } from 'core/OfferEducational/utils/createStockDataPayload'
import { extractInitialStockValues } from 'core/OfferEducational/utils/extractInitialStockValues'
import { hasStatusCodeAndErrorsCode } from 'core/OfferEducational/utils/hasStatusCode'
import { FORM_ERROR_MESSAGE } from 'core/shared/constants'
import useNotification from 'hooks/useNotification'
import { getOfferRequestInformationsAdapter } from 'pages/CollectiveOfferFromRequest/adapters/getOfferRequestInformationsAdapter'
import { queryParamsFromOfferer } from 'pages/Offers/utils/queryParamsFromOfferer'
import {
  MandatoryCollectiveOfferFromParamsProps,
  withCollectiveOfferFromParams,
} from 'screens/OfferEducational/useCollectiveOfferFromParams'
import { OfferEducationalStock } from 'screens/OfferEducationalStock/OfferEducationalStock'

import { postCollectiveOfferTemplateAdapter } from './adapters/postCollectiveOfferTemplate'

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
    let createdOfferTemplateId: number | null = null
    const isTemplate =
      values.educationalOfferType === EducationalOfferType.SHOWCASE
    if (isTemplate) {
      const response = await postCollectiveOfferTemplateAdapter({
        offerId: offer.id,
        values,
      })
      const { isOk, message } = response
      if (!isOk) {
        notify.error(message)
      }
      createdOfferTemplateId = response.payload ? response.payload.id : null
    } else {
      let response: CollectiveStockResponseModel | null = null
      try {
        if (offer.collectiveStock) {
          const patchPayload = createPatchStockDataPayload(
            values,
            offer.venue.departementCode ?? '',
            initialValues
          )
          response = await api.editCollectiveStock(
            offer.collectiveStock.id,
            patchPayload
          )
        } else {
          const stockPayload = createStockDataPayload(
            values,
            offer.venue.departementCode ?? '',
            offer.id
          )
          response = await api.createCollectiveStock(stockPayload)
        }
      } catch (error) {
        if (
          hasStatusCodeAndErrorsCode(error) &&
          error.status === 400 &&
          error.errors.code === 'EDUCATIONAL_STOCK_ALREADY_EXISTS'
        ) {
          notify.error(
            'Une erreur s’est produite. Les informations date et prix existent déjà pour cette offre.'
          )
        }
        if (isErrorAPIError(error) && error.status === 400) {
          notify.error(FORM_ERROR_MESSAGE)
        } else {
          notify.error(
            'Une erreur est survenue lors de la création de votre stock.'
          )
        }
      }
      if (response !== null) {
        setOffer({
          ...offer,
          collectiveStock: {
            ...offer.collectiveStock,
            ...response,
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
        <OfferEducationalStock
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
