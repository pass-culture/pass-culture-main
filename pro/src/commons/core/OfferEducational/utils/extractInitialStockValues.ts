import { format } from 'date-fns'

import type {
  GetCollectiveOfferRequestResponseModel,
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
} from '@/apiClient/v1/new'
import { FORMAT_HH_mm, FORMAT_ISO_DATE_ONLY } from '@/commons/utils/date'
import { getLocalDepartementDateTimeFromUtc } from '@/commons/utils/timezone'

import { DEFAULT_EAC_STOCK_FORM_VALUES } from '../constants'
import type { OfferEducationalStockFormValues } from '../types'

export const extractInitialStockValues = (
  offer: GetCollectiveOfferResponseModel,
  offerTemplate?: GetCollectiveOfferTemplateResponseModel,
  requestInformations?: GetCollectiveOfferRequestResponseModel | null
): OfferEducationalStockFormValues => {
  const { collectiveStock } = offer

  if (requestInformations) {
    const { totalStudents, totalTeachers, requestedDate } = requestInformations

    const numberOfTickets =
      totalStudents || totalTeachers
        ? (totalStudents ?? 0) + (totalTeachers ?? 0)
        : DEFAULT_EAC_STOCK_FORM_VALUES.numberOfTickets

    return {
      ...DEFAULT_EAC_STOCK_FORM_VALUES,
      numberOfTickets,
      startDate: requestedDate
        ? format(new Date(requestedDate), FORMAT_ISO_DATE_ONLY)
        : DEFAULT_EAC_STOCK_FORM_VALUES.startDate,
    }
  }

  if (!collectiveStock) {
    if (offerTemplate?.educationalPriceDetail) {
      return {
        ...DEFAULT_EAC_STOCK_FORM_VALUES,
        educationalPriceDetail: offerTemplate.educationalPriceDetail,
      }
    }
    return DEFAULT_EAC_STOCK_FORM_VALUES
  }

  const startDate = collectiveStock.startDatetime
    ? format(
        getLocalDepartementDateTimeFromUtc(
          collectiveStock.startDatetime,
          offer.venue.departementCode
        ),
        FORMAT_ISO_DATE_ONLY
      )
    : DEFAULT_EAC_STOCK_FORM_VALUES.startDate

  const endDate = collectiveStock.endDatetime
    ? format(
        getLocalDepartementDateTimeFromUtc(
          collectiveStock.endDatetime,
          offer.venue.departementCode
        ),
        FORMAT_ISO_DATE_ONLY
      )
    : DEFAULT_EAC_STOCK_FORM_VALUES.endDate

  const eventTime = collectiveStock.startDatetime
    ? format(
        getLocalDepartementDateTimeFromUtc(
          collectiveStock.startDatetime,
          offer.venue.departementCode
        ),
        FORMAT_HH_mm
      )
    : DEFAULT_EAC_STOCK_FORM_VALUES.eventTime

  const bookingLimitDate = collectiveStock.bookingLimitDatetime
    ? format(
        getLocalDepartementDateTimeFromUtc(
          collectiveStock.bookingLimitDatetime
        ),
        FORMAT_ISO_DATE_ONLY
      )
    : DEFAULT_EAC_STOCK_FORM_VALUES.bookingLimitDate

  return {
    startDate,
    endDate,
    eventTime,
    numberOfTickets:
      collectiveStock.numberOfTickets ??
      DEFAULT_EAC_STOCK_FORM_VALUES.numberOfTickets,
    totalPrice: collectiveStock.price,
    bookingLimitDate,
    educationalPriceDetail:
      collectiveStock.educationalPriceDetail ??
      DEFAULT_EAC_STOCK_FORM_VALUES.educationalPriceDetail,
  }
}
