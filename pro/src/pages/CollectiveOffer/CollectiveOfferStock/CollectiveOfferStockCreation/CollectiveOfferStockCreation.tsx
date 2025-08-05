import { api } from 'apiClient/api'
import { isErrorAPIError } from 'apiClient/helpers'
import {
  CollectiveStockResponseModel,
  GetCollectiveOfferResponseModel,
} from 'apiClient/v1'
import {
  GET_COLLECTIVE_OFFER_QUERY_KEY,
  GET_COLLECTIVE_OFFER_TEMPLATE_QUERY_KEY,
  GET_COLLECTIVE_REQUEST_INFORMATIONS_QUERY_KEY,
} from 'commons/config/swrQueryKeys'
import {
  isCollectiveOffer,
  isCollectiveOfferTemplate,
  Mode,
  OfferEducationalStockFormValues,
} from 'commons/core/OfferEducational/types'
import { computeURLCollectiveOfferId } from 'commons/core/OfferEducational/utils/computeURLCollectiveOfferId'
import { createPatchStockDataPayload } from 'commons/core/OfferEducational/utils/createPatchStockDataPayload'
import { createStockDataPayload } from 'commons/core/OfferEducational/utils/createStockDataPayload'
import { extractInitialStockValues } from 'commons/core/OfferEducational/utils/extractInitialStockValues'
import { hasStatusCodeAndErrorsCode } from 'commons/core/OfferEducational/utils/hasStatusCode'
import { FORM_ERROR_MESSAGE } from 'commons/core/shared/constants'
import { useNotification } from 'commons/hooks/useNotification'
import { queryParamsFromOfferer } from 'commons/utils/queryParamsFromOfferer'
import { CollectiveOfferLayout } from 'pages/CollectiveOffer/CollectiveOfferLayout/CollectiveOfferLayout'
import { useLocation, useNavigate } from 'react-router'
import useSWR, { useSWRConfig } from 'swr'

import {
  MandatoryCollectiveOfferFromParamsProps,
  withCollectiveOfferFromParams,
} from '../../CollectiveOffer/components/OfferEducational/useCollectiveOfferFromParams'
import { OfferEducationalStock } from '../components/OfferEducationalStock/OfferEducationalStock'

export const CollectiveOfferStockCreation = ({
  offer,
  isTemplate,
}: MandatoryCollectiveOfferFromParamsProps): JSX.Element | null => {
  const notify = useNotification()
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

  if (isCollectiveOfferTemplate(offer)) {
    throw new Error(
      'Impossible de mettre à jour les stocks d’une offre vitrine.'
    )
  }

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
            isBooked: false,
            isCancellable: offer.isCancellable,
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
        notify.error(
          'Une erreur s’est produite. Les informations dates et prix existent déjà pour cette offre.'
        )
      }
      if (
        hasStatusCodeAndErrorsCode(e) &&
        e.status === 400 &&
        e.errors.code === 'COLLECTIVE_OFFER_NOT_FOUND'
      ) {
        notify.error('Une erreur s’est produite. L’offre n’a pas été trouvée.')
      }
      if (isErrorAPIError(e) && e.status === 400) {
        notify.error(FORM_ERROR_MESSAGE)
      } else {
        notify.error(
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
