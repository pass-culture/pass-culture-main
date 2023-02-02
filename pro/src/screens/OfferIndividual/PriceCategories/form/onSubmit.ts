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
  setOffer: ((offer: IOfferIndividual | null) => void) | null
) => {
  const serializedOffer = serializePatchOffer({
    offer: offer,
    formValues: { isDuo: values.isDuo },
  })
  const { isOk: isOfferOk } = await updateIndividualOffer({
    offerId: offer.id,
    serializedOffer: serializedOffer,
  })

  const { isOk: isPriceCategoriesOk } = await postPriceCategoriesAdapter({
    offerId: offer.nonHumanizedId + '',
    requestBody: serializePriceCategories(values),
  })

  if (!isOfferOk || !isPriceCategoriesOk) {
    return
  }

  const response = await getOfferIndividualAdapter(offer.id)

  setOffer && setOffer(response.payload)
}
