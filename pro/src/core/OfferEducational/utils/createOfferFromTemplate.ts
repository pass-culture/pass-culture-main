import { useNavigate } from 'react-router-dom'

import useNotification from 'hooks/useNotification'

import getCollectiveOfferFormDataApdater from '../adapters/getCollectiveOfferFormDataAdapter'
import getCollectiveOfferTemplateAdapter from '../adapters/getCollectiveOfferTemplateAdapter'
import postCollectiveOfferAdapter from '../adapters/postCollectiveOfferAdapter'

import { computeInitialValuesFromOffer } from './computeInitialValuesFromOffer'
import { postCollectiveOfferImage } from './postCollectiveOfferImage'

export const createOfferFromTemplate = async (
  navigate: ReturnType<typeof useNavigate>,
  notify: ReturnType<typeof useNotification>,
  templateOfferId: number
) => {
  const offerTemplateResponse = await getCollectiveOfferTemplateAdapter(
    templateOfferId
  )

  if (!offerTemplateResponse.isOk) {
    return notify.error(offerTemplateResponse.message)
  }
  const offererId =
    offerTemplateResponse.payload.venue.managingOfferer.nonHumanizedId
  const result = await getCollectiveOfferFormDataApdater({
    offererId: offererId.toString(),
    offer: offerTemplateResponse.payload,
  })

  if (!result.isOk) {
    return notify.error(result.message)
  }

  const { categories, offerers } = result.payload

  const initialValues = computeInitialValuesFromOffer(
    categories,
    offerers,
    offerTemplateResponse.payload
  )

  const { isOk, message, payload } = await postCollectiveOfferAdapter({
    offer: initialValues,
    offerTemplateId: templateOfferId,
  })

  if (!isOk) {
    return notify.error(message)
  }

  await postCollectiveOfferImage({ initialValues, notify, payload })

  navigate(`/offre/collectif/${payload.id}/creation?structure=${offererId}`)
}
