import { api } from 'apiClient/api'
import { GetIndividualOfferResponseModel } from 'apiClient/v1'
import { updateIndividualOffer } from 'core/Offers/adapters'
import { serializePatchOffer } from 'core/Offers/adapters/updateIndividualOffer/serializers'

import { computeInitialValues } from './computeInitialValues'
import { serializePriceCategories } from './serializePriceCategories'
import { PriceCategoriesFormValues, PriceCategoryFormik } from './types'

export const submitToApi = async (
  values: PriceCategoriesFormValues,
  offer: GetIndividualOfferResponseModel,
  resetForm: PriceCategoryFormik['resetForm']
) => {
  const serializedOffer = serializePatchOffer({
    offer: offer,
    formValues: { isDuo: values.isDuo },
  })
  const { isOk: isOfferOk, message: offerMessage } =
    await updateIndividualOffer({
      offerId: offer.id,
      serializedOffer: serializedOffer,
    })
  if (!isOfferOk) {
    throw new Error(offerMessage)
  }

  try {
    await api.postPriceCategories(offer.id, serializePriceCategories(values))
    return {
      isOk: true,
      message: 'Vos modifications ont bien été prises en compte',
      payload: {},
    }
  } catch (error) {
    throw new Error(
      'Une erreur est survenue lors de la mise à jour de votre tarif'
    )
  }

  const updatedOffer = await api.getOffer(offer.id)
  resetForm({
    values: computeInitialValues(updatedOffer),
  })
}
