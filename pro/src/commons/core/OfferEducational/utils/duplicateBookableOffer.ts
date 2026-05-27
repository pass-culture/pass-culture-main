import type { useNavigate } from 'react-router'

import { apiNew } from '@/apiClient/api'
import { isErrorAPIError } from '@/apiClient/helpers'
import type { GetVenueResponseModel } from '@/apiClient/v1/new'
import type { OfferEducationalFormValues } from '@/commons/core/OfferEducational/types'
import type { useSnackBar } from '@/commons/hooks/useSnackBar'

import { computeInitialValuesFromOffer } from './computeInitialValuesFromOffer'
import { postCollectiveOfferImage } from './postCollectiveOfferImage'

// TODO(ahello - 31/03/25) do not make direct api calls, use swr instead
export const duplicateBookableOffer = async (
  navigate: ReturnType<typeof useNavigate>,
  snackBar: ReturnType<typeof useSnackBar>,
  offerId: number,
  venue: GetVenueResponseModel
) => {
  let initialValues: OfferEducationalFormValues
  let offererId: number | null = null
  try {
    const offerResponse = await apiNew.getCollectiveOffer({
      path: { offer_id: offerId },
    })

    offererId = offerResponse.venue.managingOfferer.id
    const { educationalOfferers } = await apiNew.listEducationalOfferers({
      query: { offererId },
    })

    const targetOfferer = educationalOfferers.find(
      (educationalOfferer) => educationalOfferer.id === offererId
    )
    const offerer = targetOfferer || null

    initialValues = computeInitialValuesFromOffer(
      offerer,
      false,
      venue,
      offerResponse
    )
  } catch {
    return snackBar.error(
      'Une erreur est survenue lors de la récupération de votre offre'
    )
  }

  try {
    const response = await apiNew.duplicateCollectiveOffer({
      path: { offer_id: offerId },
    })

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
