import { useNavigate } from 'react-router-dom'

import useNotification from 'hooks/useNotification'

import getCollectiveOfferFormDataApdater from '../adapters/getCollectiveOfferFormDataAdapter'
import getCollectiveOfferTemplateAdapter from '../adapters/getCollectiveOfferTemplateAdapter'
import postCollectiveOfferAdapter from '../adapters/postCollectiveOfferAdapter'
import postCollectiveOfferImageAdapter from '../adapters/postCollectiveOfferImageAdapter'

import { computeInitialValuesFromOffer } from './computeInitialValuesFromOffer'

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
    notify.error(result.message)
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

  const offerImageUrl = initialValues.imageUrl
  const imageErrorMessage = "Impossible de dupliquer l'image de l'offre vitrine"
  if (offerImageUrl) {
    const imageResponse = await fetch(offerImageUrl)
    if (!imageResponse) {
      return notify.error(imageErrorMessage)
    }
    const contentType = imageResponse.headers.get('content-type')
    const blob = await imageResponse.blob()
    if (!blob) {
      return notify.error(imageErrorMessage)
    }
    const imageFile = new File([blob], '', { type: contentType || '' })
    await postCollectiveOfferImageAdapter({
      offerId: payload.id,
      imageFile: imageFile,
      credit: initialValues.imageCredit || '',
      cropParams: { x: 0, y: 0, width: 1, height: 1 },
    })
  }
  navigate(`/offre/collectif/${payload.id}/creation?structure=${offererId}`)
}
