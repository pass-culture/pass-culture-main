import { api } from 'apiClient/api'
import { getIndividualOfferAdapter } from 'core/Offers/adapters'
import { IndividualOffer } from 'core/Offers/types'
import { getToday } from 'utils/date'
import { getLocalDepartementDateTimeFromUtc } from 'utils/timezone'

import { serializeStockEventEdition } from './adapters/serializers'
import upsertStocksEventAdapter from './adapters/upsertStocksEventAdapter'
import { getPriceCategoryOptions } from './getPriceCategoryOptions'
import { StockEventFormValues, StocksEventFormik } from './StockFormList/types'
import { buildInitialValues } from './StockFormList/utils'

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
      offer.venue.departementCode
    ),
  })
  if (!isUpsertStocksOk) {
    setErrors({ stocks: payload.errors })
    throw new Error(upsertStocksMessage)
  }

  const priceCategoriesOptions = getPriceCategoryOptions(offer.priceCategories)
  const today = getLocalDepartementDateTimeFromUtc(
    getToday(),
    offer.venue.departementCode
  )

  try {
    const [offerResponse, stocksResponse] = await Promise.all([
      getIndividualOfferAdapter(offer.id),
      api.getStocks(offer.id),
    ])
    const updatedStocks = stocksResponse.stocks
    if (offerResponse.isOk) {
      const updatedOffer = offerResponse.payload
      setOffer && setOffer(updatedOffer)
      resetForm({
        values: buildInitialValues({
          departementCode: updatedOffer.venue.departementCode,
          offerStocks: updatedStocks,
          today,
          lastProviderName: updatedOffer.lastProviderName,
          offerStatus: updatedOffer.status,
          priceCategoriesOptions,
        }),
      })
    } else {
      throw new Error(offerResponse.message)
    }
  } catch {
    throw new Error(
      'Une erreur est survenue lors de la récupération de vos stocks'
    )
  }
}
