import React from 'react'
import { useHistory } from 'react-router-dom'

import {
  CollectiveOffer,
  DEFAULT_EAC_STOCK_FORM_VALUES,
  EducationalOfferType,
  Mode,
  OfferEducationalStockFormValues,
} from 'core/OfferEducational'
import { computeURLCollectiveOfferId } from 'core/OfferEducational/utils/computeURLCollectiveOfferId'
import useNotification from 'hooks/useNotification'
import { RouteLeavingGuardOfferCreation } from 'new_components/RouteLeavingGuardOfferCreation'
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
      const response = await postCollectiveStockAdapter({
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
        initialValues={DEFAULT_EAC_STOCK_FORM_VALUES}
        mode={Mode.CREATION}
        offer={offer}
        onSubmit={handleSubmitStock}
      />
      <RouteLeavingGuardOfferCreation />
    </>
  )
}

export default CollectiveOfferStockCreation
