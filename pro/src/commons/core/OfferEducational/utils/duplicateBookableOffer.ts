import type { useNavigate } from 'react-router'

import { api } from '@/apiClient/api'
import { isErrorAPIError } from '@/apiClient/helpers'
import type { OfferEducationalFormValues } from '@/commons/core/OfferEducational/types'
import { serializeEducationalOfferer } from '@/commons/core/OfferEducational/utils/serializeEducationalOfferer'
import type { useSnackBar } from '@/commons/hooks/useSnackBar'

import { computeInitialValuesFromOffer } from './computeInitialValuesFromOffer'
import { postCollectiveOfferImage } from './postCollectiveOfferImage'

// TODO(ahello - 31/03/25) do not make direct api calls, use swr instead
export const duplicateBookableOffer = async (
  navigate: ReturnType<typeof useNavigate>,
  snackBar: ReturnType<typeof useSnackBar>,
  offerId: number
) => {
  let initialValues: OfferEducationalFormValues
  let offererId: number | null = null
  try {
    const offerResponse = await api.getCollectiveOffer(offerId)
    offererId = offerResponse.venue.managingOfferer.id
    const { educationalOfferers } = await api.listEducationalOfferers(offererId)
    const targetOfferer = educationalOfferers.find(
      (educationalOfferer) => educationalOfferer.id === offererId
    )
    const offerer = targetOfferer
      ? serializeEducationalOfferer(targetOfferer)
      : null

    const { venues } = await api.getVenues(null, true, offerer?.id)

    initialValues = computeInitialValuesFromOffer(
      offerer,
      false,
      venues,
      offerResponse
    )
  } catch {
    return snackBar.error(
      'Une erreur est survenue lors de la récupération de votre offre'
    )
  }

  try {
    const response = await api.duplicateCollectiveOffer(offerId)
    await postCollectiveOfferImage({ initialValues, snackBar, id: response.id })

    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    navigate(`/offre/collectif/${response.id}/creation?structure=${offererId}`)
  } catch (error) {
    const message =
      isErrorAPIError(error) && error.status === 400
        ? 'Une ou plusieurs erreurs sont présentes dans le formulaire'
        : 'Une erreur est survenue lors de la création de votre offre'
    snackBar.error(message)
  }
}
