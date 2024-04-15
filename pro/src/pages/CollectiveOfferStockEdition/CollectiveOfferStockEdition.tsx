import { useNavigate } from 'react-router-dom'

import { api } from 'apiClient/api'
import { isErrorAPIError } from 'apiClient/helpers'
import { GetCollectiveOfferResponseModel } from 'apiClient/v1'
import { AppLayout } from 'app/AppLayout'
import CollectiveOfferLayout from 'components/CollectiveOfferLayout'
import {
  Mode,
  OfferEducationalStockFormValues,
  createPatchStockDataPayload,
  extractInitialStockValues,
  getStockCollectiveOfferAdapter,
  isCollectiveOfferTemplate,
} from 'core/OfferEducational'
import { computeURLCollectiveOfferId } from 'core/OfferEducational/utils/computeURLCollectiveOfferId'
import { FORM_ERROR_MESSAGE, PATCH_SUCCESS_MESSAGE } from 'core/shared'
import useNotification from 'hooks/useNotification'
import {
  MandatoryCollectiveOfferFromParamsProps,
  withCollectiveOfferFromParams,
} from 'screens/OfferEducational/useCollectiveOfferFromParams'
import OfferEducationalStockScreen from 'screens/OfferEducationalStock'

const CollectiveOfferStockEdition = ({
  offer,
  reloadCollectiveOffer,
  isTemplate,
}: MandatoryCollectiveOfferFromParamsProps): JSX.Element => {
  const notify = useNotification()
  const navigate = useNavigate()

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
    const offerResponse = await getStockCollectiveOfferAdapter(offer.id)

    if (!offerResponse.isOk) {
      return notify.error(offerResponse.message)
    }

    await reloadCollectiveOffer()
    navigate(
      `/offre/${computeURLCollectiveOfferId(
        offer.id,
        false
      )}/collectif/recapitulatif`
    )
    notify.success(PATCH_SUCCESS_MESSAGE)
  }

  return (
    <AppLayout>
      <CollectiveOfferLayout subTitle={offer.name} isTemplate={isTemplate}>
        <OfferEducationalStockScreen
          initialValues={initialValues}
          mode={
            offer.collectiveStock?.isEducationalStockEditable
              ? Mode.EDITION
              : Mode.READ_ONLY
          }
          offer={offer}
          onSubmit={handleSubmitStock}
          reloadCollectiveOffer={reloadCollectiveOffer}
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
