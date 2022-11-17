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
  setOffer: (offer: CollectiveOffer) => void
}

const CollectiveOfferStockCreation = ({
  offer,
  setOffer,
}: OfferEducationalStockCreationProps): JSX.Element | null => {
  const notify = useNotification()
  const history = useHistory()

  const initialValues = extractInitialStockValues(offer)

  const handleSubmitStock = async (
    offer: CollectiveOffer,
    values: OfferEducationalStockFormValues
  ) => {
    let isOk: boolean
    let message: string | null
    let createdOfferTemplateId: string | null = null
    const isTemplate =
      values.educationalOfferType === EducationalOfferType.SHOWCASE
    if (isTemplate) {
      const response = await postCollectiveOfferTemplateAdapter({
        offerId: offer.id,
        values,
      })
      isOk = response.isOk
      message = response.message
      createdOfferTemplateId = response.payload ? response.payload.id : null
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

      if (offer && response.payload !== null) {
        setOffer({
          ...offer,
          collectiveStock: {
            ...offer.collectiveStock,
            ...response.payload,
            isBooked: false,
            isCancellable: offer.isCancellable,
          },
        })
      }
    }

    if (!isOk) {
      return notify.error(message)
    }

    let url = `/offre/${computeURLCollectiveOfferId(
      isTemplate && createdOfferTemplateId != null
        ? createdOfferTemplateId
        : offer.id,
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
