import { useLocation, useNavigate } from 'react-router'
import useSWR, { useSWRConfig } from 'swr'

import { api } from '@/apiClient/api'
import { isErrorAPIError } from '@/apiClient/helpers'
import type {
  CollectiveStockResponseModel,
  GetCollectiveOfferResponseModel,
} from '@/apiClient/v1'
import {
  GET_COLLECTIVE_OFFER_QUERY_KEY,
  GET_COLLECTIVE_OFFER_TEMPLATE_QUERY_KEY,
  GET_COLLECTIVE_REQUEST_INFORMATIONS_QUERY_KEY,
} from '@/commons/config/swrQueryKeys'
import {
  isCollectiveOffer,
  isCollectiveOfferTemplate,
  Mode,
  type OfferEducationalStockFormValues,
} from '@/commons/core/OfferEducational/types'
import { computeURLCollectiveOfferId } from '@/commons/core/OfferEducational/utils/computeURLCollectiveOfferId'
import { createPatchStockDataPayload } from '@/commons/core/OfferEducational/utils/createPatchStockDataPayload'
import { createStockDataPayload } from '@/commons/core/OfferEducational/utils/createStockDataPayload'
import { extractInitialStockValues } from '@/commons/core/OfferEducational/utils/extractInitialStockValues'
import { hasStatusCodeAndErrorsCode } from '@/commons/core/OfferEducational/utils/hasStatusCode'
import { FORM_ERROR_MESSAGE } from '@/commons/core/shared/constants'
import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { queryParamsFromOfferer } from '@/commons/utils/queryParamsFromOfferer'
import { CollectiveOfferLayout } from '@/pages/CollectiveOffer/CollectiveOfferLayout/CollectiveOfferLayout'

import {
  type MandatoryCollectiveOfferFromParamsProps,
  withCollectiveOfferFromParams,
} from '../../CollectiveOffer/components/OfferEducational/useCollectiveOfferFromParams'
import { OfferEducationalStock } from '../components/OfferEducationalStock/OfferEducationalStock'

export const CollectiveOfferStockCreation = ({
  offer,
  isTemplate,
}: MandatoryCollectiveOfferFromParamsProps): JSX.Element | null => {
  const snackBar = useSnackBar()
  const navigate = useNavigate()
  const location = useLocation()
  const isCreation = !location.pathname.includes('edition')
  const { requete: requestId } = queryParamsFromOfferer(location)

  const { mutate } = useSWRConfig()

  const { data: offerFromTemplate } = useSWR(
    isCollectiveOffer(offer) && offer.templateId
      ? [GET_COLLECTIVE_OFFER_TEMPLATE_QUERY_KEY, offer.templateId]
      : null,
    ([, offerTemplateIdParam]) => {
      return api.getCollectiveOfferTemplate(offerTemplateIdParam)
    }
  )

  const { data: requestInformations } = useSWR(
    () =>
      requestId
        ? [GET_COLLECTIVE_REQUEST_INFORMATIONS_QUERY_KEY, requestId]
        : null,
    ([, id]) => api.getCollectiveOfferRequest(Number(id))
  )

  assertOrFrontendError(
    !isCollectiveOfferTemplate(offer),
    '`offer` shoud not be a (collective offer) template.'
  )

  const initialValues = extractInitialStockValues(
    offer,
    offerFromTemplate,
    requestInformations
  )

  /* istanbul ignore next: DEBT, TO FIX unit test submit mock */
  const handleSubmitStock = async (
    offer: GetCollectiveOfferResponseModel,
    values: OfferEducationalStockFormValues
  ) => {
    try {
      let response: CollectiveStockResponseModel | null = null
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

      await mutate<GetCollectiveOfferResponseModel>(
        [GET_COLLECTIVE_OFFER_QUERY_KEY],
        {
          ...offer,
          collectiveStock: {
            ...offer.collectiveStock,
            ...response,
          },
        },
        { revalidate: false }
      )

      let url = `/offre/${computeURLCollectiveOfferId(
        offer.id,
        isTemplate
      )}/collectif`

      if (!isTemplate) {
        url = `${url}/visibilite${requestId ? `?requete=${requestId}` : ''}`
      } else {
        url = `${url}/creation/recapitulatif`
      }
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      navigate(url)
    } catch (e) {
      if (
        hasStatusCodeAndErrorsCode(e) &&
        e.status === 400 &&
        e.errors.code === 'EDUCATIONAL_STOCK_ALREADY_EXISTS'
      ) {
        snackBar.error(
          'Une erreur s’est produite. Les informations dates et prix existent déjà pour cette offre.'
        )
      }
      if (
        hasStatusCodeAndErrorsCode(e) &&
        e.status === 400 &&
        e.errors.code === 'COLLECTIVE_OFFER_NOT_FOUND'
      ) {
        snackBar.error(
          'Une erreur s’est produite. L’offre n’a pas été trouvée.'
        )
      }
      if (isErrorAPIError(e) && e.status === 400) {
        snackBar.error(FORM_ERROR_MESSAGE)
      } else {
        snackBar.error(
          'Une erreur est survenue lors de la création de votre stock.'
        )
      }
    }
  }

  return (
    <CollectiveOfferLayout
      subTitle={offer.name}
      isTemplate={isTemplate}
      isCreation={isCreation}
      requestId={requestId}
      offer={offer}
    >
      <OfferEducationalStock
        initialValues={initialValues}
        mode={Mode.CREATION}
        offer={offer}
        onSubmit={handleSubmitStock}
        requestId={requestId}
      />
    </CollectiveOfferLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = withCollectiveOfferFromParams(
  CollectiveOfferStockCreation
)
