import { useNavigate } from 'react-router-dom'

import { api } from 'apiClient/api'
import useNotification from 'hooks/useNotification'

import { getCollectiveOfferFormDataApdater } from '../adapters/getCollectiveOfferFormDataAdapter'
import { postCollectiveOfferAdapter } from '../adapters/postCollectiveOfferAdapter'

import { computeInitialValuesFromOffer } from './computeInitialValuesFromOffer'
import { postCollectiveOfferImage } from './postCollectiveOfferImage'

export const createOfferFromTemplate = async (
  navigate: ReturnType<typeof useNavigate>,
  notify: ReturnType<typeof useNotification>,
  templateOfferId: number,
  requestId?: string,
  isMarseilleActive?: boolean
) => {
  try {
    const offerTemplateResponse =
      await api.getCollectiveOfferTemplate(templateOfferId)

    const offererId = offerTemplateResponse.venue.managingOfferer.id
    const result = await getCollectiveOfferFormDataApdater({
      offererId: offererId,
      offer: offerTemplateResponse,
    })

    if (!result.isOk) {
      return notify.error(result.message)
    }

    const { offerers } = result.payload

    const initialValues = computeInitialValuesFromOffer(
      offerers,
      false,
      offerTemplateResponse,
      undefined,
      undefined,
      isMarseilleActive
    )
    const { isOk, message, payload } = await postCollectiveOfferAdapter({
      offer: initialValues,
      offerTemplateId: templateOfferId,
    })

    if (!isOk) {
      return notify.error(message)
    }

    await postCollectiveOfferImage({ initialValues, notify, payload })

    navigate(
      `/offre/collectif/${payload.id}/creation?structure=${offererId}${
        requestId ? `&requete=${requestId}` : ''
      }`
    )
  } catch (error) {
    return notify.error(
      'Une erreur est survenue lors de la récupération de votre offre'
    )
  }
}
