import {
  DEFAULT_EAC_STOCK_FORM_VALUES,
  EducationalOfferType,
  CollectiveOffer,
  OfferEducationalStockFormValues,
} from 'core/OfferEducational'
import { getLocalDepartementDateTimeFromUtc } from 'utils/timezone'

export const extractInitialStockValues = (
  offer: CollectiveOffer
): OfferEducationalStockFormValues => {
  const { collectiveStock } = offer
  if (!collectiveStock) {
    return DEFAULT_EAC_STOCK_FORM_VALUES
  }

  const eventDate = collectiveStock.beginningDatetime
    ? getLocalDepartementDateTimeFromUtc(
        collectiveStock.beginningDatetime,
        offer.venue.departementCode
      )
    : null
  const eventTime = collectiveStock.beginningDatetime
    ? getLocalDepartementDateTimeFromUtc(
        collectiveStock.beginningDatetime,
        offer.venue.departementCode
      )
    : null
  const bookingLimitDatetime = collectiveStock.bookingLimitDatetime
    ? getLocalDepartementDateTimeFromUtc(collectiveStock.bookingLimitDatetime)
    : null

  return {
    eventDate: eventDate ?? DEFAULT_EAC_STOCK_FORM_VALUES.eventDate,
    eventTime: eventTime ?? DEFAULT_EAC_STOCK_FORM_VALUES.eventTime,
    numberOfPlaces:
      collectiveStock.numberOfTickets ??
      DEFAULT_EAC_STOCK_FORM_VALUES.numberOfPlaces,
    totalPrice: collectiveStock.price,
    bookingLimitDatetime:
      bookingLimitDatetime ??
      DEFAULT_EAC_STOCK_FORM_VALUES.bookingLimitDatetime,
    priceDetail:
      collectiveStock.educationalPriceDetail ??
      DEFAULT_EAC_STOCK_FORM_VALUES.priceDetail,
    educationalOfferType: EducationalOfferType.CLASSIC,
  }
}
