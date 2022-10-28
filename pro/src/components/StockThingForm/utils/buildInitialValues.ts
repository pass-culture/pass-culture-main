import {
  STOCK_THING_FORM_DEFAULT_VALUES,
  IStockThingFormValues,
} from 'components/StockThingForm'
import { IOfferIndividual } from 'core/Offers/types'

export const buildInitialValues = (
  offer: IOfferIndividual
): IStockThingFormValues => {
  if (offer.stocks.length === 0) {
    return STOCK_THING_FORM_DEFAULT_VALUES
  }
  return {
    stockId: offer.stocks[0].id,
    remainingQuantity:
      offer.stocks[0].remainingQuantity?.toString() || 'unlimited',
    bookingsQuantity: offer.stocks[0].bookingsQuantity.toString(),
    quantity: offer.stocks[0].quantity?.toString() || '',
    bookingLimitDatetime: offer.stocks[0].bookingLimitDatetime
      ? new Date(offer.stocks[0].bookingLimitDatetime)
      : null,
    price: offer.stocks[0].price.toString(),
    activationCodesExpirationDateTime:
      offer.stocks[0].activationCodesExpirationDateTime,
    activationCodes: offer.stocks[0].activationCodes,
  }
}
export default buildInitialValues
