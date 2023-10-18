import {
  getIndividualOfferAdapter,
  updateIndividualOffer,
} from 'core/Offers/adapters'
import { serializePatchOffer } from 'core/Offers/adapters/updateIndividualOffer/serializers'
import { IndividualOffer } from 'core/Offers/types'

import upsertStocksThingAdapter from './adapters/upsertStocksThingAdapter'
import { StockThingFormValues, StockThingFormik } from './types'
import buildInitialValues from './utils/buildInitialValues'

export const submitToApi = async (
  values: StockThingFormValues,
  offer: IndividualOffer,
  setOffer: ((offer: IndividualOffer | null) => void) | null,
  resetForm: StockThingFormik['resetForm'],
  setErrors: StockThingFormik['setErrors']
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

  const {
    isOk: isUpsertStocksOk,
    payload,
    message: upsertStocksMessage,
  } = await upsertStocksThingAdapter({
    offerId: offer.id,
    values,
    departementCode: offer.venue.departementCode,
  })
  if (!isUpsertStocksOk) {
    setErrors(payload.errors)
    throw new Error(upsertStocksMessage)
  }

  const response = await getIndividualOfferAdapter(offer.id)
  if (response.isOk) {
    setOffer && setOffer(response.payload)
    resetForm({ values: buildInitialValues(response.payload) })
  }
}
