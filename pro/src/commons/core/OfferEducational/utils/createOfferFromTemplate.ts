import type { useNavigate } from 'react-router'

import { api } from '@/apiClient/api'
import type { GetVenueResponseModel } from '@/apiClient/v1'
import { SENT_DATA_ERROR_MESSAGE } from '@/commons/core/shared/constants'
import type { useSnackBar } from '@/commons/hooks/useSnackBar'

import { computeInitialValuesFromOffer } from './computeInitialValuesFromOffer'
import { createCollectiveOfferPayload } from './createOfferPayload'
import { postCollectiveOfferImage } from './postCollectiveOfferImage'

// TODO(ahello - 31/03/25) do not make direct api calls, use swr instead
export const createOfferFromTemplate = async (
  navigate: ReturnType<typeof useNavigate>,
  snackBar: ReturnType<typeof useSnackBar>,
  templateOfferId: number,
  venue: GetVenueResponseModel,
  requestId?: string,
  isMarseilleActive?: boolean,
  setIsCreatingNewOffer?: (isCreating: boolean) => void
) => {
  try {
    const offerTemplateResponse = await api.getCollectiveOfferTemplate({
      path: { offer_id: templateOfferId },
    })

    const offererId = offerTemplateResponse.venue.managingOfferer.id
    const targetOffererId =
      offerTemplateResponse.venue.managingOfferer.id || offererId
    const { educationalOfferers } = await api.listEducationalOfferers({
      query: { offererId: targetOffererId },
    })

    const targetOfferer = educationalOfferers.find(
      (educationalOfferer) => educationalOfferer.id === targetOffererId
    )
    const offerer = targetOfferer || null

    const initialValues = computeInitialValuesFromOffer(
      offerer,
      false,
      venue,
      offerTemplateResponse,
      undefined,
      isMarseilleActive
    )

    const payload = createCollectiveOfferPayload(initialValues, templateOfferId)

    try {
      const response = await api.createCollectiveOffer({ body: payload })

      await postCollectiveOfferImage({
        initialValues,
        snackBar,
        id: response.id,
      })

      navigate(
        `/offre/collectif/${response.id}/creation?structure=${offererId}${
          requestId ? `&requete=${requestId}` : ''
        }`
      )
    } catch {
      snackBar.error(SENT_DATA_ERROR_MESSAGE)
      setIsCreatingNewOffer?.(false)
    }
  } catch {
    setIsCreatingNewOffer?.(false)
    return snackBar.error(
      'Une erreur est survenue lors de la récupération de votre offre'
    )
  }
}
