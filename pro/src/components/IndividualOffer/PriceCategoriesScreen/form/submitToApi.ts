import { api } from 'apiClient/api'
import { isErrorAPIError, serializeApiErrors } from 'apiClient/helpers'
import { GetIndividualOfferResponseModel } from 'apiClient/v1'

import { serializePriceCategories } from './serializePriceCategories'
import { PriceCategoriesFormValues } from './types'

export const submitToApi = async (
  values: PriceCategoriesFormValues,
  offer: GetIndividualOfferResponseModel
) => {
  try {
    await api.patchOffer(offer.id, { isDuo: values.isDuo })
  } catch {
    throw new Error(
      'Une erreur est survenue lors de la création de votre offre'
    )
  }

  try {
    await api.postPriceCategories(offer.id, serializePriceCategories(values))
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
