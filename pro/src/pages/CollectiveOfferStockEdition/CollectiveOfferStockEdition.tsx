import React from 'react'
import { useNavigate } from 'react-router-dom'

import { api } from 'apiClient/api'
import { isErrorAPIError } from 'apiClient/helpers'
import { AppLayout } from 'app/AppLayout'
import CollectiveOfferLayout from 'components/CollectiveOfferLayout'
import {
  Mode,
  OfferEducationalStockFormValues,
  extractInitialStockValues,
  getStockCollectiveOfferAdapter,
  CollectiveOffer,
  isCollectiveOfferTemplate,
  createPatchStockDataPayload,
} from 'core/OfferEducational'
import { computeURLCollectiveOfferId } from 'core/OfferEducational/utils/computeURLCollectiveOfferId'
import { FORM_ERROR_MESSAGE, UNKNOWN_FAILING_RESPONSE } from 'core/shared'
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
    offer: CollectiveOffer,
    values: OfferEducationalStockFormValues
  ) => {
    if (!offer.collectiveStock) {
      return notify.error('Impossible de mettre à jour le stock.')
    }

    const offerResponse = await getStockCollectiveOfferAdapter(offer.id)

    if (!offerResponse.isOk) {
      return notify.error(offerResponse.message)
    }

    try {
      const patchStockPayload = createPatchStockDataPayload(
        values,
        offer.venue.departementCode ?? '',
        initialValues
      )
      await api.editCollectiveStock(offer.collectiveStock.id, patchStockPayload)
    } catch (e) {
      /* sendSentryCustomError(
        `error when updating stock on offer ${offer.id} ${e}`
      ) */
      if (isErrorAPIError(e) && e.status === 400) {
        return notify.error(FORM_ERROR_MESSAGE)
      } else {
        return notify.error(UNKNOWN_FAILING_RESPONSE)
      }
    }

    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    reloadCollectiveOffer()
    navigate(
      `/offre/${computeURLCollectiveOfferId(
        offer.id,
        false
      )}/collectif/recapitulatif`
    )
    notify.success('Vos modifications ont bien été enregistrées')
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
