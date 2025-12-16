import type { useNavigate } from 'react-router'

import { api } from '@/apiClient/api'
import { serializeEducationalOfferer } from '@/commons/core/OfferEducational/utils/serializeEducationalOfferer'
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
  requestId?: string,
  isMarseilleActive?: boolean,
  setIsCreatingNewOffer?: (isCreating: boolean) => void
) => {
  try {
    const offerTemplateResponse =
      await api.getCollectiveOfferTemplate(templateOfferId)

    const offererId = offerTemplateResponse.venue.managingOfferer.id
    const targetOffererId =
      offerTemplateResponse.venue.managingOfferer.id || offererId
    const { educationalOfferers } =
      await api.listEducationalOfferers(targetOffererId)
    const targetOfferer = educationalOfferers.find(
      (educationalOfferer) => educationalOfferer.id === targetOffererId
    )
    const offerers = targetOfferer
      ? serializeEducationalOfferer(targetOfferer)
      : null
    const { venues } = await api.getVenues(null, true, targetOffererId)

    const initialValues = computeInitialValuesFromOffer(
      offerers,
      false,
      venues,
      offerTemplateResponse,
      undefined,
      isMarseilleActive
    )

    const payload = createCollectiveOfferPayload(initialValues, templateOfferId)

    try {
      const response = await api.createCollectiveOffer(payload)
      await postCollectiveOfferImage({
        initialValues,
        snackBar,
        id: response.id,
      })

      // eslint-disable-next-line @typescript-eslint/no-floating-promises
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
