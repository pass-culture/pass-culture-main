import { format } from 'date-fns'

import { GetCollectiveOfferRequestResponseModel } from 'apiClient/v1/models/GetCollectiveOfferRequestResponseModel'
import {
  DEFAULT_EAC_STOCK_FORM_VALUES,
  EducationalOfferType,
  CollectiveOffer,
  CollectiveOfferTemplate,
  OfferEducationalStockFormValues,
} from 'core/OfferEducational'
import { FORMAT_HH_mm, FORMAT_ISO_DATE_ONLY } from 'utils/date'
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
        ? format(new Date(requestedDate), FORMAT_ISO_DATE_ONLY)
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
    ? format(
        getLocalDepartementDateTimeFromUtc(
          collectiveStock.beginningDatetime,
          offer.venue.departementCode
        ),
        FORMAT_ISO_DATE_ONLY
      )
    : ''
  const eventTime = collectiveStock.beginningDatetime
    ? format(
        getLocalDepartementDateTimeFromUtc(
          collectiveStock.beginningDatetime,
          offer.venue.departementCode
        ),
        FORMAT_HH_mm
      )
    : ''
  const bookingLimitDatetime = collectiveStock.bookingLimitDatetime
    ? format(
        getLocalDepartementDateTimeFromUtc(
          collectiveStock.bookingLimitDatetime
        ),
        FORMAT_ISO_DATE_ONLY
      )
    : ''

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
