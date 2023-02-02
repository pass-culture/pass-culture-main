import {
  getOfferIndividualAdapter,
  updateIndividualOffer,
} from 'core/Offers/adapters'
import { serializePatchOffer } from 'core/Offers/adapters/updateIndividualOffer/serializers'
import { IOfferIndividual } from 'core/Offers/types'

import postPriceCategoriesAdapter from '../adapter/postPriceCategoriesAdapter'
import { serializePriceCategories } from '../adapter/serializePriceCategories'

import { PriceCategoriesFormValues } from './types'

export const onSubmit = async (
  values: PriceCategoriesFormValues,
  offer: IOfferIndividual,
  setOffer: ((offer: IOfferIndividual | null) => void) | null,
  notifyError: (msg: string) => void
): Promise<boolean> => {
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
    notifyError(offerMessage)
    return false
  }

  const { isOk: isPriceCategoriesOk, message: priceCategoriesMessage } =
    await postPriceCategoriesAdapter({
      offerId: offer.nonHumanizedId + '',
      requestBody: serializePriceCategories(values),
    })

  if (!isPriceCategoriesOk) {
    notifyError(priceCategoriesMessage)
    return false
  }

  const response = await getOfferIndividualAdapter(offer.id)
  setOffer && setOffer(response.payload)

  return true
}
