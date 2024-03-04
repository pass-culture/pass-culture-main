import { api } from 'apiClient/api'
import { isErrorAPIError, serializeApiErrors } from 'apiClient/helpers'
import { GetIndividualOfferResponseModel } from 'apiClient/v1'
import { updateIndividualOffer } from 'core/Offers/adapters'
import { serializePatchOffer } from 'core/Offers/adapters/updateIndividualOffer/serializers'

import { serializeStockThingList } from './serializers'
import { StockThingFormValues, StockThingFormik } from './types'
import buildInitialValues from './utils/buildInitialValues'

export const submitToApi = async (
  values: StockThingFormValues,
  offer: GetIndividualOfferResponseModel,
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

  try {
    await api.upsertStocks({
      offerId: offer.id,
      stocks: serializeStockThingList(values, offer.venue.departementCode),
    })

    const [offerResponse, stockResponse] = await Promise.all([
      api.getOffer(offer.id),
      api.getStocks(offer.id),
    ])
    resetForm({
      values: buildInitialValues(offerResponse, stockResponse.stocks),
    })
  } catch (error) {
    let formErrors = {}
    /* istanbul ignore next */
    if (isErrorAPIError(error)) {
      formErrors = error.body
    }
    setErrors(serializeApiErrors(formErrors))
    throw new Error(
      'Une erreur est survenue lors de la mise à jour de votre stock'
    )
  }
}
