import type { ScopedMutator } from 'swr'

import { api } from '@/apiClient/api'
import { isErrorAPIError, serializeApiErrors } from '@/apiClient/helpers'
import type { GetIndividualOfferResponseModel } from '@/apiClient/v1'
import { GET_OFFER_QUERY_KEY } from '@/commons/config/swrQueryKeys'

import { serializePriceCategories } from './serializePriceCategories'
import type { PriceCategoriesFormValues } from './types'

export const submitToApi = async (
  values: PriceCategoriesFormValues,
  offer: GetIndividualOfferResponseModel,
  mutate: ScopedMutator
) => {
  try {
    await mutate(
      [GET_OFFER_QUERY_KEY, offer.id],
      api.patchOffer(offer.id, { isDuo: values.isDuo }),
      { revalidate: false }
    )
  } catch {
    throw new Error(
      'Une erreur est survenue lors de la création de votre offre'
    )
  }

  try {
    await mutate(
      [GET_OFFER_QUERY_KEY, offer.id],
      api.postPriceCategories(offer.id, serializePriceCategories(values)),
      { revalidate: false }
    )
  } catch (error) {
    if (isErrorAPIError(error)) {
      const serializedApiErrors = serializeApiErrors(error.body)

      if (serializedApiErrors.url) {
        throw new Error(
          'Vous n’avez pas renseigné l’URL d’accès à l’offre dans la page Informations pratiques.'
        )
      }
    }
    throw new Error(
      'Une erreur est survenue lors de la mise à jour de votre tarif'
    )
  }
}
