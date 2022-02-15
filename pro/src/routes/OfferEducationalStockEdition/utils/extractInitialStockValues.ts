import {
  DEFAULT_EAC_STOCK_FORM_VALUES,
  OfferEducationalStockFormValues,
  GetStockOfferSuccessPayload,
  EducationalOfferType,
} from 'core/OfferEducational'
import { Stock } from 'custom_types'
import { getLocalDepartementDateTimeFromUtc } from 'utils/timezone'

export const extractInitialStockValues = (
  stock: Stock | null,
  offer: GetStockOfferSuccessPayload
): OfferEducationalStockFormValues => {
  if (!stock) {
    return DEFAULT_EAC_STOCK_FORM_VALUES
  }

  return {
    eventDate:
      getLocalDepartementDateTimeFromUtc(
        stock.beginningDatetime,
        offer.venueDepartmentCode
      ) ?? DEFAULT_EAC_STOCK_FORM_VALUES.eventDate,
    eventTime:
      getLocalDepartementDateTimeFromUtc(
        stock.beginningDatetime,
        offer.venueDepartmentCode
      ) ?? DEFAULT_EAC_STOCK_FORM_VALUES.eventTime,
    numberOfPlaces:
      stock.numberOfTickets ?? DEFAULT_EAC_STOCK_FORM_VALUES.numberOfPlaces,
    totalPrice: stock.price,
    bookingLimitDatetime:
      getLocalDepartementDateTimeFromUtc(stock.bookingLimitDatetime) ??
      DEFAULT_EAC_STOCK_FORM_VALUES.bookingLimitDatetime,
    priceDetail:
      stock.educationalPriceDetail ?? DEFAULT_EAC_STOCK_FORM_VALUES.priceDetail,
    educationalOfferType: offer.isShowcase
      ? EducationalOfferType.SHOWCASE
      : EducationalOfferType.CLASSIC,
  }
}
