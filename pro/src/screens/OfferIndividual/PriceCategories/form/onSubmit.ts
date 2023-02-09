import type { FormikState } from 'formik'

import {
  getOfferIndividualAdapter,
  updateIndividualOffer,
} from 'core/Offers/adapters'
import { serializePatchOffer } from 'core/Offers/adapters/updateIndividualOffer/serializers'
import { IOfferIndividual } from 'core/Offers/types'

import postPriceCategoriesAdapter from '../adapters/postPriceCategoriesAdapter'
import { serializePriceCategories } from '../adapters/serializePriceCategories'

import { computeInitialValues } from './computeInitialValues'
import { PriceCategoriesFormValues } from './types'

export const onSubmit = async (
  values: PriceCategoriesFormValues,
  offer: IOfferIndividual,
  setOffer: ((offer: IOfferIndividual | null) => void) | null,
  resetForm: (
    nextState?: Partial<FormikState<PriceCategoriesFormValues>> | undefined
  ) => void
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
      offerId: offer.nonHumanizedId + '',
      requestBody: serializePriceCategories(values),
    })

  if (!isPriceCategoriesOk) {
    throw new Error(priceCategoriesMessage)
  }

  const response = await getOfferIndividualAdapter(offer.id)
  if (response.isOk) {
    /* istanbul ignore next */
    const updatedOffer = response.payload
    setOffer && setOffer(updatedOffer)
    resetForm({
      values: computeInitialValues(updatedOffer),
    })
  }
}
