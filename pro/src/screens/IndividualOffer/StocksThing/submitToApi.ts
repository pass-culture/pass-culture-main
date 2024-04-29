import { api } from 'apiClient/api'
import {
  getHumanReadableApiError,
  isErrorAPIError,
  serializeApiErrors,
} from 'apiClient/helpers'
import { GetIndividualOfferResponseModel } from 'apiClient/v1'
import { updateIndividualOffer } from 'core/Offers/adapters/updateIndividualOffer/updateIndividualOffer'

import { serializeStockThingList } from './adapters/serializers'
import { StockThingFormValues, StockThingFormik } from './types'
import buildInitialValues from './utils/buildInitialValues'

export const submitToApi = async (
  values: StockThingFormValues,
  offer: GetIndividualOfferResponseModel,
  resetForm: StockThingFormik['resetForm'],
  setErrors: StockThingFormik['setErrors']
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
    await api.upsertStocks({
      offerId: offer.id,
      stocks: serializeStockThingList(values, offer.venue.departementCode),
    })
  } catch (error) {
    if (isErrorAPIError(error)) {
      const serializedApiErrors = serializeApiErrors(error.body)
      setErrors(serializedApiErrors)
      // for this error, we want to display a custom error on the price field
      if (serializedApiErrors.priceLimitationRule) {
        setErrors({ price: 'Non valide' })
      }
    }
    throw new Error(getHumanReadableApiError(error))
  }

  const [offerResponse, stockResponse] = await Promise.all([
    api.getOffer(offer.id),
    api.getStocks(offer.id),
  ])
  resetForm({
    values: buildInitialValues(offerResponse, stockResponse.stocks),
  })
}
