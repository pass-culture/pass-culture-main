import { api } from 'apiClient/api'
import { GetIndividualOfferResponseModel } from 'apiClient/v1'
import { updateIndividualOffer } from 'core/Offers/adapters'
import { serializePatchOffer } from 'core/Offers/adapters/updateIndividualOffer/serializers'

import postPriceCategoriesAdapter from '../adapters/postPriceCategoriesAdapter'
import { serializePriceCategories } from '../adapters/serializePriceCategories'

import { computeInitialValues } from './computeInitialValues'
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

  const { isOk: isPriceCategoriesOk, message: priceCategoriesMessage } =
    await postPriceCategoriesAdapter({
      offerId: offer.id,
      requestBody: serializePriceCategories(values),
    })
  if (!isPriceCategoriesOk) {
    throw new Error(priceCategoriesMessage)
  }

  const updatedOffer = await api.getOffer(offer.id)
  resetForm({
    values: computeInitialValues(updatedOffer),
  })
}
