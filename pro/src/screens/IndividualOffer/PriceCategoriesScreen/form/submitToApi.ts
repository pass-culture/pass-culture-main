import { api } from 'apiClient/api'
import { GetIndividualOfferResponseModel } from 'apiClient/v1'

import { computeInitialValues } from './computeInitialValues'
import { serializePriceCategories } from './serializePriceCategories'
import { PriceCategoriesFormValues, PriceCategoryFormik } from './types'

export const submitToApi = async (
  values: PriceCategoriesFormValues,
  offer: GetIndividualOfferResponseModel,
  resetForm: PriceCategoryFormik['resetForm']
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
  } catch {
    throw new Error(
      'Une erreur est survenue lors de la mise à jour de votre tarif'
    )
  }

  const updatedOffer = await api.getOffer(offer.id)
  resetForm({
    values: computeInitialValues(updatedOffer),
  })
}
