import { GetCollectiveOfferRequestResponseModel } from 'apiClient/v1/models/GetCollectiveOfferRequestResponseModel'
import {
  DEFAULT_EAC_STOCK_FORM_VALUES,
  EducationalOfferType,
  CollectiveOffer,
  CollectiveOfferTemplate,
  OfferEducationalStockFormValues,
} from 'core/OfferEducational'
import { getLocalDepartementDateTimeFromUtc } from 'utils/timezone'

export const extractInitialStockValues = (
  offer: CollectiveOffer,
  offerTemplate?: CollectiveOfferTemplate,
  requestInformations?: GetCollectiveOfferRequestResponseModel | null
): OfferEducationalStockFormValues => {
  const { collectiveStock } = offer

  if (requestInformations) {
    const { totalStudents, totalTeachers, requestedDate } = requestInformations

    const numberOfPlaces =
      totalStudents || totalTeachers
        ? (totalStudents ?? 0) + (totalTeachers ?? 0)
        : DEFAULT_EAC_STOCK_FORM_VALUES.numberOfPlaces

    return {
      ...DEFAULT_EAC_STOCK_FORM_VALUES,
      numberOfPlaces,
      eventDate: requestedDate
        ? new Date(requestedDate)
        : DEFAULT_EAC_STOCK_FORM_VALUES.eventDate,
    }
  }

  if (!collectiveStock) {
    if (offerTemplate?.educationalPriceDetail) {
      return {
        ...DEFAULT_EAC_STOCK_FORM_VALUES,
        priceDetail: offerTemplate.educationalPriceDetail,
      }
    }
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
