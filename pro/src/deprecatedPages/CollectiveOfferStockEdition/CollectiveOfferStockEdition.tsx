import React from 'react'
import { useNavigate } from 'react-router-dom'

import CollectiveOfferLayout from 'components/CollectiveOfferLayout'
import PageTitle from 'components/PageTitle/PageTitle'
import {
  Mode,
  OfferEducationalStockFormValues,
  extractInitialStockValues,
  getStockCollectiveOfferAdapter,
  CollectiveOffer,
  isCollectiveOfferTemplate,
} from 'core/OfferEducational'
import { computeURLCollectiveOfferId } from 'core/OfferEducational/utils/computeURLCollectiveOfferId'
import useNotification from 'hooks/useNotification'
import {
  MandatoryCollectiveOfferFromParamsProps,
  withCollectiveOfferFromParams,
} from 'screens/OfferEducational/useCollectiveOfferFromParams'
import OfferEducationalStockScreen from 'screens/OfferEducationalStock'

import patchCollectiveStockAdapter from './adapters/patchCollectiveStockAdapter'

const CollectiveOfferStockEdition = ({
  offer,
  reloadCollectiveOffer,
  isTemplate,
}: MandatoryCollectiveOfferFromParamsProps): JSX.Element => {
  const notify = useNotification()
  const navigate = useNavigate()

  if (isCollectiveOfferTemplate(offer)) {
    throw new Error("Impossible de mettre à jour le stock d'une offre vitrine.")
  }

  const initialValues = extractInitialStockValues(offer)

  const handleSubmitStock = async (
    offer: CollectiveOffer,
    values: OfferEducationalStockFormValues
  ) => {
    if (!offer.collectiveStock) {
      return notify.error('Impossible de mettre à jour le stock.')
    }

    const stockResponse = await patchCollectiveStockAdapter({
      offer,
      stockId: offer.collectiveStock.nonHumanizedId,
      values,
      initialValues,
    })
    const offerResponse = await getStockCollectiveOfferAdapter(
      offer.nonHumanizedId
    )

    if (!stockResponse.isOk) {
      return notify.error(stockResponse.message)
    }

    if (!offerResponse.isOk) {
      return notify.error(offerResponse.message)
    }

    reloadCollectiveOffer()
    navigate(
      `/offre/${computeURLCollectiveOfferId(
        offer.nonHumanizedId,
        false
      )}/collectif/recapitulatif`
    )
    notify.success(stockResponse.message)
  }

  return (
    <CollectiveOfferLayout subTitle={offer.name} isTemplate={isTemplate}>
      <PageTitle title="Date et prix" />
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
  )
}

export default withCollectiveOfferFromParams(CollectiveOfferStockEdition)
