import React from 'react'
import { useHistory } from 'react-router-dom'

import RouteLeavingGuardOfferCreation from 'components/RouteLeavingGuardOfferCreation'
import {
  CollectiveOffer,
  EducationalOfferType,
  extractInitialStockValues,
  Mode,
  OfferEducationalStockFormValues,
} from 'core/OfferEducational'
import { computeURLCollectiveOfferId } from 'core/OfferEducational/utils/computeURLCollectiveOfferId'
import useNotification from 'hooks/useNotification'
import patchCollectiveStockAdapter from 'pages/CollectiveOfferStockEdition/adapters/patchCollectiveStockAdapter'
import OfferEducationalStockScreen from 'screens/OfferEducationalStock'

import postCollectiveOfferTemplateAdapter from './adapters/postCollectiveOfferTemplate'
import postCollectiveStockAdapter from './adapters/postCollectiveStock'

interface OfferEducationalStockCreationProps {
  offer: CollectiveOffer
}

const CollectiveOfferStockCreation = ({
  offer,
}: OfferEducationalStockCreationProps): JSX.Element | null => {
  const notify = useNotification()
  const history = useHistory()

  const initialValues = extractInitialStockValues(
    offer.collectiveStock ?? null,
    offer
  )

  const handleSubmitStock = async (
    offer: CollectiveOffer,
    values: OfferEducationalStockFormValues
  ) => {
    let isOk: boolean
    let message: string | null
    let payload: { id: string } | null
    const isTemplate =
      values.educationalOfferType === EducationalOfferType.SHOWCASE

    if (isTemplate) {
      const response = await postCollectiveOfferTemplateAdapter({
        offerId: offer.id,
        values,
      })
      isOk = response.isOk
      message = response.message
      payload = response.payload
    } else {
      const response = offer.collectiveStock
        ? await patchCollectiveStockAdapter({
            offer,
            stockId: offer.collectiveStock.id,
            values,
            initialValues,
          })
        : await postCollectiveStockAdapter({
            offer,
            values,
          })
      isOk = response.isOk
      message = response.message
      payload = response.payload
    }

    if (!isOk) {
      return notify.error(message)
    }

    let url = `/offre/${computeURLCollectiveOfferId(
      isTemplate && payload ? payload.id : offer.id,
      isTemplate
    )}/collectif`

    if (!isTemplate) {
      url = `${url}/visibilite`
    } else {
      url = `${url}/creation/recapitulatif`
    }
    history.push(url)
  }

  return (
    <>
      <OfferEducationalStockScreen
        initialValues={initialValues}
        mode={Mode.CREATION}
        offer={offer}
        onSubmit={handleSubmitStock}
      />
      <RouteLeavingGuardOfferCreation />
    </>
  )
}

export default CollectiveOfferStockCreation
