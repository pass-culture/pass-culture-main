import { useNavigate } from 'react-router-dom'
import { useSWRConfig } from 'swr'

import { api } from 'apiClient/api'
import { isErrorAPIError } from 'apiClient/helpers'
import { GetCollectiveOfferResponseModel } from 'apiClient/v1'
import { AppLayout } from 'app/AppLayout'
import { CollectiveOfferLayout } from 'components/CollectiveOfferLayout/CollectiveOfferLayout'
import { GET_COLLECTIVE_OFFER_QUERY_KEY } from 'config/swrQueryKeys'
import {
  isCollectiveOfferTemplate,
  OfferEducationalStockFormValues,
  Mode,
} from 'core/OfferEducational/types'
import { computeURLCollectiveOfferId } from 'core/OfferEducational/utils/computeURLCollectiveOfferId'
import { createPatchStockDataPayload } from 'core/OfferEducational/utils/createPatchStockDataPayload'
import { extractInitialStockValues } from 'core/OfferEducational/utils/extractInitialStockValues'
import {
  FORM_ERROR_MESSAGE,
  PATCH_SUCCESS_MESSAGE,
} from 'core/shared/constants'
import useNotification from 'hooks/useNotification'
import {
  MandatoryCollectiveOfferFromParamsProps,
  withCollectiveOfferFromParams,
} from 'screens/OfferEducational/useCollectiveOfferFromParams'
import { OfferEducationalStock } from 'screens/OfferEducationalStock/OfferEducationalStock'

const CollectiveOfferStockEdition = ({
  offer,
  isTemplate,
}: MandatoryCollectiveOfferFromParamsProps): JSX.Element => {
  const notify = useNotification()
  const navigate = useNavigate()
  const { mutate } = useSWRConfig()

  if (isCollectiveOfferTemplate(offer)) {
    throw new Error('Impossible de mettre à jour le stock d’une offre vitrine.')
  }

  const initialValues = extractInitialStockValues(offer)

  const handleSubmitStock = async (
    offer: GetCollectiveOfferResponseModel,
    values: OfferEducationalStockFormValues
  ) => {
    if (!offer.collectiveStock) {
      return notify.error('Impossible de mettre à jour le stock.')
    }

    const stockPayload = createPatchStockDataPayload(
      values,
      offer.venue.departementCode ?? '',
      initialValues
    )
    try {
      await api.editCollectiveStock(offer.collectiveStock.id, stockPayload)
    } catch (error) {
      if (isErrorAPIError(error) && error.status === 400) {
        notify.error(FORM_ERROR_MESSAGE)
      } else {
        notify.error(
          'Une erreur est survenue lors de la mise à jour de votre stock.'
        )
      }
    }

    await mutate([GET_COLLECTIVE_OFFER_QUERY_KEY, offer.id])
    navigate(
      `/offre/${computeURLCollectiveOfferId(
        offer.id,
        false
      )}/collectif/recapitulatif`
    )
    notify.success(PATCH_SUCCESS_MESSAGE)
  }

  return (
    <AppLayout layout="sticky-actions">
      <CollectiveOfferLayout subTitle={offer.name} isTemplate={isTemplate}>
        <OfferEducationalStock
          initialValues={initialValues}
          mode={
            offer.collectiveStock?.isEducationalStockEditable
              ? Mode.EDITION
              : Mode.READ_ONLY
          }
          offer={offer}
          onSubmit={handleSubmitStock}
        />
      </CollectiveOfferLayout>
    </AppLayout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = withCollectiveOfferFromParams(
  CollectiveOfferStockEdition
)
