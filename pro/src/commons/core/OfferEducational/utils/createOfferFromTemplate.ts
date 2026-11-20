import type { useNavigate } from 'react-router'
import useSWRMutation from 'swr/mutation'

import { api } from '@/apiClient/api'
import type { GetVenueResponseModel } from '@/apiClient/v1'
import {
  CREATE_COLLECTIVE_OFFER_QUERY_KEY,
  GET_COLLECTIVE_OFFER_TEMPLATE_QUERY_KEY,
  GET_EDUCATIONAL_OFFERERS_QUERY_KEY,
} from '@/commons/config/swrQueryKeys'
import { SENT_DATA_ERROR_MESSAGE } from '@/commons/core/shared/constants'
import type { useSnackBar } from '@/commons/hooks/useSnackBar'

import { computeInitialValuesFromOffer } from './computeInitialValuesFromOffer'
import { createCollectiveOfferPayload } from './createOfferPayload'
import { postCollectiveOfferImage } from './postCollectiveOfferImage'

export const useCreateOfferFromTemplate = () => {
  const { trigger: getCollectiveOfferTemplate } = useSWRMutation(
    GET_COLLECTIVE_OFFER_TEMPLATE_QUERY_KEY,
    (_key: string, { arg }: { arg: number }) =>
      api.getCollectiveOfferTemplate({ path: { offer_id: arg } })
  )
  const { trigger: listEducationalOfferers } = useSWRMutation(
    GET_EDUCATIONAL_OFFERERS_QUERY_KEY,
    (_key: string, { arg }: { arg: number }) =>
      api.listEducationalOfferers({ query: { offererId: arg } })
  )
  const { trigger: createCollectiveOffer } = useSWRMutation(
    CREATE_COLLECTIVE_OFFER_QUERY_KEY,
    (
      _key: string,
      { arg }: { arg: ReturnType<typeof createCollectiveOfferPayload> }
    ) => api.createCollectiveOffer({ body: arg })
  )

  return async (
    navigate: ReturnType<typeof useNavigate>,
    snackBar: ReturnType<typeof useSnackBar>,
    templateOfferId: number,
    venue: GetVenueResponseModel,
    requestId?: string,
    isMarseilleActive?: boolean,
    setIsCreatingNewOffer?: (isCreating: boolean) => void
  ) => {
    try {
      const offerTemplateResponse =
        await getCollectiveOfferTemplate(templateOfferId)

      const offererId = offerTemplateResponse.venue.managingOfferer.id
      const targetOffererId =
        offerTemplateResponse.venue.managingOfferer.id || offererId
      const { educationalOfferers } =
        await listEducationalOfferers(targetOffererId)

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

      const payload = createCollectiveOfferPayload(
        initialValues,
        templateOfferId
      )

      try {
        const response = await createCollectiveOffer(payload)

        await postCollectiveOfferImage({
          initialValues,
          snackBar,
          id: response.id,
        })

        await navigate(
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
}
