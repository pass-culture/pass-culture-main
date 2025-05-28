import {
  GetIndividualOfferWithAddressResponseModel,
  GetOfferStockResponseModel,
} from 'apiClient/v1'
import { isDateValid } from 'commons/utils/date'
import { getLocalDepartementDateTimeFromUtc } from 'commons/utils/timezone'
import { getDepartmentCode } from 'components/IndividualOffer/utils/getDepartmentCode'

import { STOCK_THING_FORM_DEFAULT_VALUES } from '../constants'
import { StockThingFormValues } from '../types'

export const buildInitialValues = (
  offer: GetIndividualOfferWithAddressResponseModel,
  stocks: GetOfferStockResponseModel[]
): StockThingFormValues => {
  if (stocks.length === 0) {
    return STOCK_THING_FORM_DEFAULT_VALUES
  }

  return {
    stockId: stocks[0].id,
    remainingQuantity: stocks[0].remainingQuantity?.toString() || 'unlimited',
    bookingsQuantity: stocks[0].bookingsQuantity.toString(),
    quantity: stocks[0].quantity ?? null,
    bookingLimitDatetime: stocks[0].bookingLimitDatetime
      ? getLocalDepartementDateTimeFromUtc(
          stocks[0].bookingLimitDatetime,
          getDepartmentCode(offer)
        )
      : null,
    price: stocks[0].price,
    activationCodesExpirationDatetime: isDateValid(
      stocks[0].activationCodesExpirationDatetime
    )
      ? new Date(stocks[0].activationCodesExpirationDatetime)
      : undefined,
    activationCodes: [],
    isDuo: offer.isDuo,
  }
}
