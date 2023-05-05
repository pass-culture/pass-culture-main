import { useNavigate } from 'react-router-dom'

import useNotification from 'hooks/useNotification'

import getCollectiveOfferAdapter from '../adapters/getCollectiveOfferAdapter'
import getCollectiveOfferFormDataApdater from '../adapters/getCollectiveOfferFormDataAdapter'
import postCollectiveDuplicateOfferAdapter from '../adapters/postCollectiveDuplicateOfferAdapter'

import { computeInitialValuesFromOffer } from './computeInitialValuesFromOffer'
import { postCollectiveOfferImage } from './postCollectiveOfferImage'

export const createOfferFromBookableOffer = async (
  navigate: ReturnType<typeof useNavigate>,
  notify: ReturnType<typeof useNotification>,
  offerId: number
) => {
  const offerResponse = await getCollectiveOfferAdapter(offerId)

  if (!offerResponse.isOk) {
    return notify.error(offerResponse.message)
  }
  const offererId = offerResponse.payload.venue.managingOfferer.nonHumanizedId
  const result = await getCollectiveOfferFormDataApdater({
    offererId: offererId.toString(),
    offer: offerResponse.payload,
  })

  if (!result.isOk) {
    return notify.error(result.message)
  }

  const { categories, offerers } = result.payload

  const initialValues = computeInitialValuesFromOffer(
    categories,
    offerers,
    offerResponse.payload
  )

  const { isOk, message, payload } = await postCollectiveDuplicateOfferAdapter({
    offerId,
  })

  if (!isOk) {
    return notify.error(message)
  }

  await postCollectiveOfferImage({ initialValues, notify, payload })

  navigate(`/offre/collectif/${payload.id}/creation?structure=${offererId}`)
}
