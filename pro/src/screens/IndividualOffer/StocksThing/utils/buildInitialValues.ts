import { format } from 'date-fns'

import {
  GetIndividualOfferResponseModel,
  GetOfferStockResponseModel,
} from 'apiClient/v1'
import { FORMAT_ISO_DATE_ONLY, isDateValid } from 'utils/date'
import { getLocalDepartementDateTimeFromUtc } from 'utils/timezone'

import { STOCK_THING_FORM_DEFAULT_VALUES } from '../constants'
import { StockThingFormValues } from '../types'

export const buildInitialValues = (
  offer: GetIndividualOfferResponseModel,
  stocks: GetOfferStockResponseModel[]
): StockThingFormValues => {
  if (!stocks[0]) {
    return STOCK_THING_FORM_DEFAULT_VALUES
  }

  return {
    stockId: stocks[0].id,
    remainingQuantity: stocks[0].remainingQuantity?.toString() || 'unlimited',
    bookingsQuantity: stocks[0].bookingsQuantity.toString(),
    quantity: stocks[0].quantity === undefined ? '' : stocks[0].quantity,
    bookingLimitDatetime: stocks[0].bookingLimitDatetime
      ? format(
          getLocalDepartementDateTimeFromUtc(
            stocks[0].bookingLimitDatetime,
            offer.venue.departementCode
          ),
          FORMAT_ISO_DATE_ONLY
        )
      : '',
    price: stocks[0].price,
    activationCodesExpirationDatetime: isDateValid(
      stocks[0].activationCodesExpirationDatetime
    )
      ? format(
          new Date(stocks[0].activationCodesExpirationDatetime),
          FORMAT_ISO_DATE_ONLY
        )
      : '',
    activationCodes: [],
    isDuo: offer.isDuo,
  }
}
