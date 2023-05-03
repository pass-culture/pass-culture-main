import { IOfferIndividual } from 'core/Offers/types'
import { getLocalDepartementDateTimeFromUtc } from 'utils/timezone'

import { STOCK_THING_FORM_DEFAULT_VALUES, IStockThingFormValues } from '../'

export const buildInitialValues = (
  offer: IOfferIndividual
): IStockThingFormValues => {
  if (offer.stocks.length === 0) {
    return STOCK_THING_FORM_DEFAULT_VALUES
  }
  return {
    stockId: offer.stocks[0].nonHumanizedId,
    remainingQuantity:
      offer.stocks[0].remainingQuantity?.toString() || 'unlimited',
    bookingsQuantity: offer.stocks[0].bookingsQuantity.toString(),
    quantity:
      offer.stocks[0].quantity === undefined ? '' : offer.stocks[0].quantity,
    bookingLimitDatetime: offer.stocks[0].bookingLimitDatetime
      ? getLocalDepartementDateTimeFromUtc(
          offer.stocks[0].bookingLimitDatetime,
          offer.venue.departmentCode
        )
      : null,
    price: offer.stocks[0].price,
    activationCodesExpirationDatetime:
      offer.stocks[0].activationCodesExpirationDatetime,
    activationCodes: offer.stocks[0].activationCodes,
    isDuo: offer.isDuo,
  }
}
export default buildInitialValues
