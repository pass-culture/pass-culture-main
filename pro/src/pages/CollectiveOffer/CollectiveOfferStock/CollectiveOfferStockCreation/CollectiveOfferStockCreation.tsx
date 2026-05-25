import { useLocation, useNavigate } from 'react-router'
import useSWR, { useSWRConfig } from 'swr'

import { apiNew } from '@/apiClient/api'
import { isErrorAPIError } from '@/apiClient/helpers'
import type {
  CollectiveStockResponseModel,
  GetCollectiveOfferResponseModel,
} from '@/apiClient/v1/new'
import {
  GET_COLLECTIVE_OFFER_QUERY_KEY,
  GET_COLLECTIVE_OFFER_TEMPLATE_QUERY_KEY,
  GET_COLLECTIVE_REQUEST_INFORMATIONS_QUERY_KEY,
} from '@/commons/config/swrQueryKeys'
import {
  type CollectiveOfferStockFormValues,
  Mode,
} from '@/commons/core/OfferEducational/types'
import { createPatchStockDataPayload } from '@/commons/core/OfferEducational/utils/createPatchStockDataPayload'
import { createStockDataPayload } from '@/commons/core/OfferEducational/utils/createStockDataPayload'
import { extractInitialStockValues } from '@/commons/core/OfferEducational/utils/extractInitialStockValues'
import { hasStatusCodeAndErrorsCode } from '@/commons/core/OfferEducational/utils/hasStatusCode'
import { FORM_ERROR_MESSAGE } from '@/commons/core/shared/constants'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { queryParamsFromOfferer } from '@/commons/utils/queryParamsFromOfferer'
import { CollectiveOfferLayout } from '@/pages/CollectiveOffer/CollectiveOfferLayout/CollectiveOfferLayout'

import {
  type CollectiveOfferFromParamsProps,
  withOnlyCollectiveOfferFromParams,
} from '../../CollectiveOffer/components/OfferEducational/useCollectiveOfferFromParams'
import { OfferEducationalStock } from '../components/OfferEducationalStock/OfferEducationalStock'

export const CollectiveOfferStockCreation = ({
  offer,
}: CollectiveOfferFromParamsProps): JSX.Element | null => {
  const snackBar = useSnackBar()
  const navigate = useNavigate()
  const location = useLocation()
  const isCreation = !location.pathname.includes('edition')
  const { requete: requestId } = queryParamsFromOfferer(location)

  const { mutate } = useSWRConfig()

  const { data: offerFromTemplate } = useSWR(
    offer.templateId
      ? [GET_COLLECTIVE_OFFER_TEMPLATE_QUERY_KEY, offer.templateId]
      : null,
    ([, offerTemplateIdParam]) => {
      return apiNew.getCollectiveOfferTemplate({
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
      apiNew.getCollectiveOfferRequest({
        path: { request_id: Number(id) },
      })
  )

  const initialValues = extractInitialStockValues(
    offer,
    offerFromTemplate,
    requestInformations
  )

  /* istanbul ignore next: DEBT, TO FIX unit test submit mock */
  const handleSubmitStock = async (
    offer: GetCollectiveOfferResponseModel,
    values: CollectiveOfferStockFormValues
  ) => {
    try {
      let response: CollectiveStockResponseModel | null = null
      if (offer.collectiveStock) {
        const patchPayload = createPatchStockDataPayload(
          values,
          offer.venue.departementCode ?? '',
          initialValues
        )
        response = await apiNew.editCollectiveStock({
          path: { collective_stock_id: offer.collectiveStock.id },
          body: patchPayload,
        })
      } else {
        const stockPayload = createStockDataPayload(
          values,
          offer.venue.departementCode ?? '',
          offer.id
        )
        response = await apiNew.createCollectiveStock({ body: stockPayload })
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

      const nexStepUrl = `/offre/${offer.id}/collectif/etablissement`
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      navigate(requestId ? `${nexStepUrl}?requete=${requestId}` : nexStepUrl)
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
      isTemplate={false}
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
export const Component = withOnlyCollectiveOfferFromParams(
  CollectiveOfferStockCreation
)
