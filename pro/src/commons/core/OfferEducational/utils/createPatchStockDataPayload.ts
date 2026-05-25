import type { CollectiveStockEditionBodyModel } from '@/apiClient/v1/new'
import { isEqual } from '@/commons/utils/isEqual'

import type { OfferEducationalStockFormValues } from '../types'
import {
  buildBookingLimitDatetimeForStockPayload,
  buildDatetimeForStockPayload,
} from './buildDatetimesForStockPayload'

type OfferEducationalStockFormValuesForSerializer = {
  startDate: string
  endDate: string
  eventTime: string
  numberOfTickets: number
  totalPrice: number
  bookingLimitDate: string
  educationalPriceDetail: string
}

const serializer = {
  startDate: (
    values: OfferEducationalStockFormValuesForSerializer,
    changedValues: CollectiveStockEditionBodyModel,
    departmentCode: string
  ) => ({
    ...changedValues,
    startDatetime: buildDatetimeForStockPayload(
      values.startDate,
      values.eventTime,
      departmentCode
    ),
  }),
  endDate: (
    values: OfferEducationalStockFormValuesForSerializer,
    changedValues: CollectiveStockEditionBodyModel,
    departmentCode: string
  ) => ({
    ...changedValues,
    endDatetime: buildDatetimeForStockPayload(
      values.endDate,
      values.eventTime,
      departmentCode
    ),
  }),
  eventTime: (
    values: OfferEducationalStockFormValuesForSerializer,
    changedValues: CollectiveStockEditionBodyModel,
    departmentCode: string
  ) => ({
    ...changedValues,
    startDatetime: buildDatetimeForStockPayload(
      values.startDate,
      values.eventTime,
      departmentCode
    ),
    endDatetime: buildDatetimeForStockPayload(
      values.endDate,
      values.eventTime,
      departmentCode
    ),
  }),
  numberOfTickets: (
    values: OfferEducationalStockFormValuesForSerializer,
    changedValues: CollectiveStockEditionBodyModel
  ) => ({
    ...changedValues,
    numberOfTickets: values.numberOfTickets,
  }),
  totalPrice: (
    values: OfferEducationalStockFormValuesForSerializer,
    changedValues: CollectiveStockEditionBodyModel
  ) => ({
    ...changedValues,
    totalPrice: values.totalPrice,
  }),
  bookingLimitDate: (
    values: OfferEducationalStockFormValuesForSerializer,
    changedValues: CollectiveStockEditionBodyModel,
    departmentCode: string
  ) => ({
    ...changedValues,
    bookingLimitDatetime: buildBookingLimitDatetimeForStockPayload(
      values.startDate,
      values.eventTime,
      values.bookingLimitDate,
      departmentCode
    ),
  }),
  educationalPriceDetail: (
    values: OfferEducationalStockFormValuesForSerializer,
    changedValues: CollectiveStockEditionBodyModel
  ) => ({
    ...changedValues,
    educationalPriceDetail: values.educationalPriceDetail,
  }),
}

const valuesIsOfferEducationalStockFormValuesForSerializer = (
  values: OfferEducationalStockFormValues
): values is OfferEducationalStockFormValuesForSerializer => {
  return (
    typeof values.numberOfTickets === 'number' &&
    typeof values.totalPrice === 'number'
  )
}

export const createPatchStockDataPayload = (
  values: OfferEducationalStockFormValues,
  departmentCode: string,
  initialValues: OfferEducationalStockFormValues
): CollectiveStockEditionBodyModel => {
  let changedValues: CollectiveStockEditionBodyModel = {}

  if (valuesIsOfferEducationalStockFormValuesForSerializer(values)) {
    ;(
      Object.keys(initialValues) as (keyof OfferEducationalStockFormValues)[]
    ).forEach((key) => {
      if (!isEqual(values[key], initialValues[key])) {
        changedValues = serializer[key](values, changedValues, departmentCode)
      }
    })
  }

  return changedValues
}
