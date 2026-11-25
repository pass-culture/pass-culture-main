import type { useNavigate } from 'react-router'
import useSWRMutation from 'swr/mutation'

import { api } from '@/apiClient/api'
import { isErrorAPIError } from '@/apiClient/helpers'
import type { GetVenueResponseModel } from '@/apiClient/v1'
import {
  DUPLICATE_COLLECTIVE_OFFER_QUERY_KEY,
  GET_COLLECTIVE_OFFER_QUERY_KEY,
  GET_EDUCATIONAL_OFFERERS_QUERY_KEY,
} from '@/commons/config/swrQueryKeys'
import type { OfferEducationalFormValues } from '@/commons/core/OfferEducational/types'
import type { useSnackBar } from '@/commons/hooks/useSnackBar'

import { computeInitialValuesFromOffer } from './computeInitialValuesFromOffer'
import { postCollectiveOfferImage } from './postCollectiveOfferImage'

export const useDuplicateBookableOffer = () => {
  const { trigger: getCollectiveOffer } = useSWRMutation(
    GET_COLLECTIVE_OFFER_QUERY_KEY,
    (_key: string, { arg }: { arg: number }) =>
      api.getCollectiveOffer({ path: { offer_id: arg } })
  )
  const { trigger: listEducationalOfferers } = useSWRMutation(
    GET_EDUCATIONAL_OFFERERS_QUERY_KEY,
    (_key: string, { arg }: { arg: number }) =>
      api.listEducationalOfferers({ query: { offererId: arg } })
  )
  const { trigger: duplicateCollectiveOffer } = useSWRMutation(
    DUPLICATE_COLLECTIVE_OFFER_QUERY_KEY,
    (_key: string, { arg }: { arg: number }) =>
      api.duplicateCollectiveOffer({ path: { offer_id: arg } })
  )

  return async (
    navigate: ReturnType<typeof useNavigate>,
    snackBar: ReturnType<typeof useSnackBar>,
    offerId: number,
    venue: GetVenueResponseModel
  ) => {
    let initialValues: OfferEducationalFormValues
    let offererId: number | null = null
    try {
      const offerResponse = await getCollectiveOffer(offerId)

      offererId = offerResponse.venue.managingOfferer.id
      const { educationalOfferers } = await listEducationalOfferers(offererId)

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
      const response = await duplicateCollectiveOffer(offerId)

      await postCollectiveOfferImage({
        initialValues,
        snackBar,
        id: response.id,
      })

      await navigate(
        `/offre/collectif/${response.id}/creation?structure=${offererId}`
      )
    } catch (error) {
      const message =
        isErrorAPIError(error) && error.status === 400
          ? 'Une ou plusieurs erreurs sont présentes dans le formulaire'
          : 'Une erreur est survenue lors de la création de votre offre'
      snackBar.error(message)
    }
  }
}
