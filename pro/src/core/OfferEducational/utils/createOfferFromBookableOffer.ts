import { useNavigate } from 'react-router-dom'

import { api } from 'apiClient/api'
import { serializeEducationalOfferers } from 'core/OfferEducational/utils/serializeEducationalOfferers'
import useNotification from 'hooks/useNotification'

import { postCollectiveDuplicateOfferAdapter } from '../adapters/postCollectiveDuplicateOfferAdapter'

import { computeInitialValuesFromOffer } from './computeInitialValuesFromOffer'
import { postCollectiveOfferImage } from './postCollectiveOfferImage'

export const createOfferFromBookableOffer = async (
  navigate: ReturnType<typeof useNavigate>,
  notify: ReturnType<typeof useNotification>,
  offerId: number
) => {
  try {
    const offerResponse = await api.getCollectiveOffer(offerId)
    const offererId = offerResponse.venue.managingOfferer.id
    const targetOffererId = offerResponse.venue.managingOfferer.id || offererId
    const { educationalOfferers } =
      await api.listEducationalOfferers(targetOffererId)
    const offerers = serializeEducationalOfferers(educationalOfferers)

    const initialValues = computeInitialValuesFromOffer(
      offerers,
      false,
      offerResponse
    )

    const { isOk, message, payload } =
      await postCollectiveDuplicateOfferAdapter({
        offerId,
      })

    if (!isOk) {
      return notify.error(message)
    }

    await postCollectiveOfferImage({ initialValues, notify, payload })

    navigate(`/offre/collectif/${payload.id}/creation?structure=${offererId}`)
  } catch (error) {
    notify.error(
      'Une erreur est survenue lors de la récupération de votre offre'
    )
  }
}
