import { useNavigate } from 'react-router-dom'

import { api } from 'apiClient/api'
import { SENT_DATA_ERROR_MESSAGE } from 'core/shared/constants'
import useNotification from 'hooks/useNotification'

import { getCollectiveOfferFormDataApdater } from '../adapters/getCollectiveOfferFormDataAdapter'

import { computeInitialValuesFromOffer } from './computeInitialValuesFromOffer'
import { createCollectiveOfferPayload } from './createOfferPayload'
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
    const payload = createCollectiveOfferPayload(initialValues, templateOfferId)

    try {
      const response = await api.createCollectiveOffer(payload)
      await postCollectiveOfferImage({
        initialValues,
        notify,
        payload: response,
      })

      navigate(
        `/offre/collectif/${response.id}/creation?structure=${offererId}${
          requestId ? `&requete=${requestId}` : ''
        }`
      )
    } catch (error) {
      notify.error(SENT_DATA_ERROR_MESSAGE)
    }
  } catch (error) {
    return notify.error(
      'Une erreur est survenue lors de la récupération de votre offre'
    )
  }
}
