import { format } from 'date-fns'

import {
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
  GetCollectiveOfferRequestResponseModel,
} from 'apiClient/v1'
import { FORMAT_HH_mm, FORMAT_ISO_DATE_ONLY } from 'utils/date'
import { getLocalDepartementDateTimeFromUtc } from 'utils/timezone'

import { DEFAULT_EAC_STOCK_FORM_VALUES } from '../constants'
import { OfferEducationalStockFormValues, EducationalOfferType } from '../types'

export const extractInitialStockValues = (
  offer: GetCollectiveOfferResponseModel,
  offerTemplate?: GetCollectiveOfferTemplateResponseModel,
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
      startDatetime: requestedDate
        ? format(new Date(requestedDate), FORMAT_ISO_DATE_ONLY)
        : DEFAULT_EAC_STOCK_FORM_VALUES.startDatetime,
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

  const startDatetime = collectiveStock.startDatetime
    ? format(
        getLocalDepartementDateTimeFromUtc(
          collectiveStock.startDatetime,
          offer.venue.departementCode
        ),
        FORMAT_ISO_DATE_ONLY
      )
    : DEFAULT_EAC_STOCK_FORM_VALUES.startDatetime

  const endDatetime = collectiveStock.endDatetime
    ? format(
        getLocalDepartementDateTimeFromUtc(
          collectiveStock.endDatetime,
          offer.venue.departementCode
        ),
        FORMAT_ISO_DATE_ONLY
      )
    : DEFAULT_EAC_STOCK_FORM_VALUES.endDatetime

  const eventTime = collectiveStock.startDatetime
    ? format(
        getLocalDepartementDateTimeFromUtc(
          collectiveStock.startDatetime,
          offer.venue.departementCode
        ),
        FORMAT_HH_mm
      )
    : DEFAULT_EAC_STOCK_FORM_VALUES.eventTime

  const bookingLimitDatetime = collectiveStock.bookingLimitDatetime
    ? format(
        getLocalDepartementDateTimeFromUtc(
          collectiveStock.bookingLimitDatetime
        ),
        FORMAT_ISO_DATE_ONLY
      )
    : DEFAULT_EAC_STOCK_FORM_VALUES.bookingLimitDatetime

  return {
    startDatetime,
    endDatetime,
    eventTime,
    numberOfPlaces:
      collectiveStock.numberOfTickets ??
      DEFAULT_EAC_STOCK_FORM_VALUES.numberOfPlaces,
    totalPrice: collectiveStock.price,
    bookingLimitDatetime,
    priceDetail:
      collectiveStock.educationalPriceDetail ??
      DEFAULT_EAC_STOCK_FORM_VALUES.priceDetail,
    educationalOfferType: EducationalOfferType.CLASSIC,
  }
}
