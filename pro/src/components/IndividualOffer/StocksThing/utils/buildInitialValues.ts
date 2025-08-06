import { format } from 'date-fns'

import {
  GetIndividualOfferWithAddressResponseModel,
  GetOfferStockResponseModel,
} from '@/apiClient//v1'
import { FORMAT_ISO_DATE_ONLY, isDateValid } from '@/commons/utils/date'
import { getDepartmentCode } from '@/commons/utils/getDepartmentCode'
import { getLocalDepartementDateTimeFromUtc } from '@/commons/utils/timezone'

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
    quantity: stocks[0].quantity ?? undefined,
    bookingLimitDatetime: stocks[0].bookingLimitDatetime
      ? format(
          getLocalDepartementDateTimeFromUtc(
            stocks[0].bookingLimitDatetime,
            getDepartmentCode(offer)
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
