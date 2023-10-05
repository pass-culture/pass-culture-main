import { getIndividualOfferAdapter } from 'core/Offers/adapters'
import { IndividualOffer } from 'core/Offers/types'
import { getToday } from 'utils/date'
import { getLocalDepartementDateTimeFromUtc } from 'utils/timezone'

import { serializeStockEventEdition } from './adapters/serializers'
import upsertStocksEventAdapter from './adapters/upsertStocksEventAdapter'
import { StockEventFormValues, StocksEventFormik } from './StockFormList/types'
import { buildInitialValues } from './StockFormList/utils'
import { getPriceCategoryOptions } from './StocksEventEdition'

export const submitToApi = async (
  allStockValues: StockEventFormValues[],
  offer: IndividualOffer,
  setOffer: ((offer: IndividualOffer | null) => void) | null,
  resetForm: StocksEventFormik['resetForm'],
  setErrors: StocksEventFormik['setErrors']
) => {
  const {
    isOk: isUpsertStocksOk,
    payload,
    message: upsertStocksMessage,
  } = await upsertStocksEventAdapter({
    offerId: offer.id,
    stocks: serializeStockEventEdition(
      allStockValues,
      offer.venue.departmentCode
    ),
  })
  if (!isUpsertStocksOk) {
    setErrors({ stocks: payload.errors })
    throw new Error(upsertStocksMessage)
  }

  const priceCategoriesOptions = getPriceCategoryOptions(offer.priceCategories)
  const today = getLocalDepartementDateTimeFromUtc(
    getToday(),
    offer.venue.departmentCode
  )

  const response = await getIndividualOfferAdapter(offer.id)
  if (response.isOk) {
    const updatedOffer = response.payload
    setOffer && setOffer(updatedOffer)
    resetForm({
      values: buildInitialValues({
        departmentCode: updatedOffer.venue.departmentCode,
        offerStocks: updatedOffer.stocks,
        today,
        lastProviderName: updatedOffer.lastProviderName,
        offerStatus: updatedOffer.status,
        priceCategoriesOptions,
      }),
    })
  }
}
