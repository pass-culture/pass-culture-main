import {
  getIndividualOfferAdapter,
  updateIndividualOffer,
} from 'core/Offers/adapters'
import { serializePatchOffer } from 'core/Offers/adapters/updateIndividualOffer/serializers'
import { IndividualOffer } from 'core/Offers/types'

import postPriceCategoriesAdapter from '../adapters/postPriceCategoriesAdapter'
import { serializePriceCategories } from '../adapters/serializePriceCategories'

import { computeInitialValues } from './computeInitialValues'
import { PriceCategoriesFormValues, PriceCategoryFormik } from './types'

export const submitToApi = async (
  values: PriceCategoriesFormValues,
  offer: IndividualOffer,
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

  const response = await getIndividualOfferAdapter(offer.id)
  if (response.isOk) {
    const updatedOffer = response.payload
    resetForm({
      values: computeInitialValues(updatedOffer),
    })
  }
}
