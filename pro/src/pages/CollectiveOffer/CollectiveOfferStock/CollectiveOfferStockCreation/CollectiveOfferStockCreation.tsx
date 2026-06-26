import { format } from 'date-fns'
import { useLocation, useNavigate } from 'react-router'
import useSWR, { useSWRConfig } from 'swr'

import { api } from '@/apiClient/api'
import { isErrorAPIError } from '@/apiClient/helpers'
import type {
  CollectiveStockCreationBodyModel,
  CollectiveStockResponseModel,
  GetCollectiveOfferResponseModel,
} from '@/apiClient/v1'
import {
  GET_COLLECTIVE_OFFER_QUERY_KEY,
  GET_COLLECTIVE_OFFER_TEMPLATE_QUERY_KEY,
  GET_COLLECTIVE_REQUEST_INFORMATIONS_QUERY_KEY,
} from '@/commons/config/swrQueryKeys'
import { Mode } from '@/commons/core/OfferEducational/types'
import { hasStatusCodeAndErrorsCode } from '@/commons/core/OfferEducational/utils/hasStatusCode'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { FORMAT_ISO_DATE_ONLY } from '@/commons/utils/date'
import { queryParamsFromOfferer } from '@/commons/utils/queryParamsFromOfferer'
import { CollectiveOfferLayout } from '@/pages/CollectiveOffer/CollectiveOfferLayout/CollectiveOfferLayout'

import {
  type CollectiveOfferFromParamsProps,
  withOnlyCollectiveOfferFromParams,
} from '../../CollectiveOffer/components/OfferEducational/useCollectiveOfferFromParams'
import { CollectiveOfferStockForm } from '../components/CollectiveOfferStockForm/CollectiveOfferStockForm'
import { OfferEducationalStock } from '../components/OfferEducationalStock/OfferEducationalStock'

function isComplete(
  stock: Partial<CollectiveStockCreationBodyModel>,
  isNewCollectivePriceEnabled: boolean
): stock is CollectiveStockCreationBodyModel {
  const allKeys: (keyof CollectiveStockCreationBodyModel)[] = [
    'bookingLimitDatetime',
    'endDatetime',
    'numberOfTickets',
    'startDatetime',
  ]
  if (isNewCollectivePriceEnabled) {
    allKeys.push('numberOfTeachers')
  } else {
    allKeys.push('price', 'priceDetail')
  }
  return allKeys.every((key) => key in stock && stock[key] !== undefined)
}

function handleStockError(
  e: unknown,
  onError: (message: string) => void
): void {
  console.error(e)
  if (hasStatusCodeAndErrorsCode(e) && e.status === 400) {
    const errorMessages: Partial<Record<string, string>> = {
      EDUCATIONAL_STOCK_ALREADY_EXISTS:
        'Une erreur s’est produite. Les informations dates et prix existent déjà pour cette offre.',
      COLLECTIVE_OFFER_NOT_FOUND:
        'Une erreur s’est produite. L’offre n’a pas été trouvée.',
    }
    const message = errorMessages[e.errors.code]
    if (message) {
      onError(message)
      return
    }
  }
  if (isErrorAPIError(e) && e.status < 500) {
    throw e
  }
  onError('Une erreur est survenue lors de la création de votre stock.')
}

function buildCreateStockBody(
  newCollectiveStock: CollectiveStockCreationBodyModel,
  offerId: number,
  isNewCollectivePriceEnabled: boolean
): CollectiveStockCreationBodyModel {
  return {
    ...newCollectiveStock,
    offerId,
    servicePrice: isNewCollectivePriceEnabled
      ? newCollectiveStock.servicePrice
      : undefined,
    collectiveAdditionalFees: isNewCollectivePriceEnabled
      ? newCollectiveStock.collectiveAdditionalFees
      : undefined,
  }
}

export const CollectiveOfferStockCreation = ({
  offer,
}: CollectiveOfferFromParamsProps): JSX.Element | null => {
  const snackBar = useSnackBar()
  const navigate = useNavigate()
  const location = useLocation()
  const isCreation = !location.pathname.includes('edition')
  const { requete: requestId } = queryParamsFromOfferer(location)
  const { mutate } = useSWRConfig()
  const isNewCollectivePriceEnabled = useActiveFeature(
    'WIP_ENABLE_NEW_COLLECTIVE_PRICE_DETAILS'
  )

  const { data: offerFromTemplate } = useSWR(
    offer.templateId
      ? [GET_COLLECTIVE_OFFER_TEMPLATE_QUERY_KEY, offer.templateId]
      : null,
    ([, offerTemplateIdParam]) => {
      return api.getCollectiveOfferTemplate({
        path: { offer_id: offerTemplateIdParam },
      })
    }
  )

  const { data: requestInformations } = useSWR(
    () =>
      requestId
        ? [GET_COLLECTIVE_REQUEST_INFORMATIONS_QUERY_KEY, requestId]
        : null,
    ([, id]) =>
      api.getCollectiveOfferRequest({
        path: { request_id: Number(id) },
      })
  )

  const initialStock: Partial<CollectiveStockResponseModel> =
    offer.collectiveStock || {}

  if (requestInformations) {
    const { totalStudents, totalTeachers, requestedDate } = requestInformations
    if (totalStudents || totalTeachers) {
      initialStock.numberOfTickets = (totalStudents ?? 0) + (totalTeachers ?? 0)
    }
    if (requestedDate) {
      initialStock.startDatetime = format(
        new Date(requestedDate),
        FORMAT_ISO_DATE_ONLY
      )
    }
  }

  if (!offer.collectiveStock && offerFromTemplate?.priceDetail) {
    initialStock.priceDetail = offerFromTemplate.priceDetail
  }

  const departementCode = offer.venue.departementCode ?? ''

  const stepUrls = {
    previous: `/offre/collectif/${offer.id}/creation`,
    next: `/offre/${offer.id}/collectif/etablissement`,
  }
  if (isNewCollectivePriceEnabled) {
    stepUrls.next = `/offre/${offer.id}/collectif/informations-pratiques`
  }
  if (requestId) {
    stepUrls.previous += `?requete=${requestId}`
    stepUrls.next += `?requete=${requestId}`
  }

  const handleSubmitStock = async (
    newCollectiveStock: Partial<CollectiveStockCreationBodyModel>
  ) => {
    if (isNewCollectivePriceEnabled) {
      delete newCollectiveStock.priceDetail
    }
    try {
      let response: CollectiveStockResponseModel | null = null
      if (offer.collectiveStock) {
        response = await api.editCollectiveStock({
          path: { collective_stock_id: offer.collectiveStock.id },
          body: newCollectiveStock,
        })
      } else if (isComplete(newCollectiveStock, isNewCollectivePriceEnabled)) {
        response = await api.createCollectiveStock({
          body: buildCreateStockBody(
            newCollectiveStock,
            offer.id,
            isNewCollectivePriceEnabled
          ),
        })
      } else {
        throw new Error('Missing required values')
      }
      await mutate<GetCollectiveOfferResponseModel>(
        [GET_COLLECTIVE_OFFER_QUERY_KEY, Number(offer.id)],
        {
          ...offer,
          collectiveStock: {
            ...offer.collectiveStock,
            ...response,
          },
        },
        { revalidate: false }
      )

      navigate(stepUrls.next)
    } catch (e) {
      handleStockError(e, snackBar.error)
    }
  }

  return (
    <CollectiveOfferLayout
      subTitle={offer.name}
      isTemplate={false}
      isCreation={isCreation}
      requestId={requestId}
      offer={offer}
    >
      {isNewCollectivePriceEnabled ? (
        <CollectiveOfferStockForm
          initialStock={initialStock}
          departementCode={departementCode}
          mode={Mode.CREATION}
          allowedActions={offer.allowedActions}
          onSubmit={handleSubmitStock}
          goBackLink={stepUrls.previous}
        />
      ) : (
        <OfferEducationalStock
          initialStock={initialStock}
          departementCode={departementCode}
          mode={Mode.CREATION}
          allowedActions={offer.allowedActions}
          onSubmit={handleSubmitStock}
          goBackLink={stepUrls.previous}
        />
      )}
    </CollectiveOfferLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = withOnlyCollectiveOfferFromParams(
  CollectiveOfferStockCreation
)
