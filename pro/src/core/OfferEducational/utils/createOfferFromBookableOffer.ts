import { useNavigate } from 'react-router-dom'

import { api } from 'apiClient/api'
import { isErrorAPIError } from 'apiClient/helpers'
import { OfferEducationalFormValues } from 'core/OfferEducational/types'
import { serializeEducationalOfferers } from 'core/OfferEducational/utils/serializeEducationalOfferers'
import useNotification from 'hooks/useNotification'

import { computeInitialValuesFromOffer } from './computeInitialValuesFromOffer'
import { postCollectiveOfferImage } from './postCollectiveOfferImage'

export const createOfferFromBookableOffer = async (
  navigate: ReturnType<typeof useNavigate>,
  notify: ReturnType<typeof useNotification>,
  offerId: number
) => {
  let initialValues: OfferEducationalFormValues
  let offererId = null
  try {
    const offerResponse = await api.getCollectiveOffer(offerId)
    offererId = offerResponse.venue.managingOfferer.id
    const { educationalOfferers } = await api.listEducationalOfferers(offererId)
    const offerers = serializeEducationalOfferers(educationalOfferers)

    initialValues = computeInitialValuesFromOffer(
      offerers,
      false,
      offerResponse
    )
  } catch (error) {
    return notify.error(
      'Une erreur est survenue lors de la récupération de votre offre'
    )
  }

  try {
    const response = await api.duplicateCollectiveOffer(offerId)
    await postCollectiveOfferImage({ initialValues, notify, id: response.id })

    navigate(`/offre/collectif/${response.id}/creation?structure=${offererId}`)
  } catch (error) {
    const message =
      isErrorAPIError(error) && error.status === 400
        ? 'Une ou plusieurs erreurs sont présentes dans le formulaire'
        : 'Une erreur est survenue lors de la création de votre offre'
    notify.error(message)
  }
}
