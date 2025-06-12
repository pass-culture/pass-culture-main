import { format } from 'date-fns'

import {
  GetIndividualOfferWithAddressResponseModel,
  GetOfferStockResponseModel,
} from 'apiClient/v1'
import {
  isDateValid,
  formatShortDateForInput,
  FORMAT_ISO_DATE_ONLY,
} from 'commons/utils/date'
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
    stockId: stocks.length > 0 ? stocks[0].id : undefined,
    remainingQuantity: stocks[0].remainingQuantity?.toString() || 'unlimited',
    bookingsQuantity: stocks[0].bookingsQuantity.toString(),
    quantity: stocks[0].quantity ?? null,
    bookingLimitDatetime: isDateValid(stocks[0].bookingLimitDatetime)
      ? format(
          getLocalDepartementDateTimeFromUtc(
            new Date(stocks[0].bookingLimitDatetime),
            getDepartmentCode(offer)
          ),
          FORMAT_ISO_DATE_ONLY
        )
      : '',
    price: stocks[0].price,
    activationCodesExpirationDatetime: isDateValid(
      stocks[0].activationCodesExpirationDatetime
    )
      ? formatShortDateForInput(
          new Date(stocks[0].activationCodesExpirationDatetime)
        )
      : '',
    activationCodes: [],
    isDuo: offer.isDuo,
  }
}
