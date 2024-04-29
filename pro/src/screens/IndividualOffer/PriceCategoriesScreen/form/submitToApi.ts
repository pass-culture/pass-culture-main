import { api } from 'apiClient/api'
import { GetIndividualOfferResponseModel } from 'apiClient/v1'
import { updateIndividualOffer } from 'core/Offers/adapters/updateIndividualOffer/updateIndividualOffer'

import { serializePriceCategories } from '../adapters/serializePriceCategories'

import { computeInitialValues } from './computeInitialValues'
import { PriceCategoriesFormValues, PriceCategoryFormik } from './types'

export const submitToApi = async (
  values: PriceCategoriesFormValues,
  offer: GetIndividualOfferResponseModel,
  resetForm: PriceCategoryFormik['resetForm']
) => {
  const { isOk: isOfferOk, message: offerMessage } =
    await updateIndividualOffer({
      offerId: offer.id,
      serializedOffer: { isDuo: values.isDuo },
    })
  if (!isOfferOk) {
    throw new Error(offerMessage)
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
