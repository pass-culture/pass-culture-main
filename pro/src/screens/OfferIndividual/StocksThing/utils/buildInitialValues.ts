import { format } from 'date-fns'

import { OfferIndividual } from 'core/Offers/types'
import { FORMAT_ISO_DATE_ONLY, isDateValid } from 'utils/date'
import { getLocalDepartementDateTimeFromUtc } from 'utils/timezone'

import { STOCK_THING_FORM_DEFAULT_VALUES, StockThingFormValues } from '../'

const buildInitialValues = (offer: OfferIndividual): StockThingFormValues => {
  if (offer.stocks.length === 0) {
    return STOCK_THING_FORM_DEFAULT_VALUES
  }
  return {
    stockId: offer.stocks[0].id,
    remainingQuantity:
      offer.stocks[0].remainingQuantity?.toString() || 'unlimited',
    bookingsQuantity: offer.stocks[0].bookingsQuantity.toString(),
    quantity:
      offer.stocks[0].quantity === undefined ? '' : offer.stocks[0].quantity,
    bookingLimitDatetime: offer.stocks[0].bookingLimitDatetime
      ? format(
          getLocalDepartementDateTimeFromUtc(
            offer.stocks[0].bookingLimitDatetime,
            offer.venue.departmentCode
          ),
          FORMAT_ISO_DATE_ONLY
        )
      : '',
    price: offer.stocks[0].price,
    activationCodesExpirationDatetime: isDateValid(
      offer.stocks[0].activationCodesExpirationDatetime
    )
      ? format(
          offer.stocks[0].activationCodesExpirationDatetime,
          FORMAT_ISO_DATE_ONLY
        )
      : '',
    activationCodes: offer.stocks[0].activationCodes,
    isDuo: offer.isDuo,
  }
}

export default buildInitialValues
