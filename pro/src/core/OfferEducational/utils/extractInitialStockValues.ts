import { CollectiveStockResponseModel } from 'apiClient/v1'
import {
  DEFAULT_EAC_STOCK_FORM_VALUES,
  EducationalOfferType,
  CollectiveOffer,
  CollectiveOfferTemplate,
  OfferEducationalStockFormValues,
} from 'core/OfferEducational'
import { getLocalDepartementDateTimeFromUtc } from 'utils/timezone'

export const extractInitialStockValues = (
  stock: CollectiveStockResponseModel | null,
  offer: CollectiveOffer | CollectiveOfferTemplate
): OfferEducationalStockFormValues => {
  if (!stock) {
    return DEFAULT_EAC_STOCK_FORM_VALUES
  }

  const eventDate = stock.beginningDatetime
    ? getLocalDepartementDateTimeFromUtc(
        stock.beginningDatetime,
        offer.venue.departementCode
      )
    : null
  const eventTime = stock.beginningDatetime
    ? getLocalDepartementDateTimeFromUtc(
        stock.beginningDatetime,
        offer.venue.departementCode
      )
    : null
  const bookingLimitDatetime = stock.bookingLimitDatetime
    ? getLocalDepartementDateTimeFromUtc(stock.bookingLimitDatetime)
    : null

  return {
    eventDate: eventDate ?? DEFAULT_EAC_STOCK_FORM_VALUES.eventDate,
    eventTime: eventTime ?? DEFAULT_EAC_STOCK_FORM_VALUES.eventTime,
    numberOfPlaces:
      stock.numberOfTickets ?? DEFAULT_EAC_STOCK_FORM_VALUES.numberOfPlaces,
    totalPrice: stock.price,
    bookingLimitDatetime:
      bookingLimitDatetime ??
      DEFAULT_EAC_STOCK_FORM_VALUES.bookingLimitDatetime,
    priceDetail:
      stock.educationalPriceDetail ?? DEFAULT_EAC_STOCK_FORM_VALUES.priceDetail,
    educationalOfferType: EducationalOfferType.CLASSIC,
  }
}
