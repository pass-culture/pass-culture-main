import { CollectiveStockEditionBodyModel } from '@/apiClient//v1'
import { isEqual } from '@/commons/utils/isEqual'

import { OfferEducationalStockFormValues } from '../types'
import {
  buildBookingLimitDatetimeForStockPayload,
  buildDatetimeForStockPayload,
} from './buildDatetimesForStockPayload'

type OfferEducationalStockFormValuesForSerializer = {
  startDatetime: string
  endDatetime: string
  eventTime: string
  numberOfPlaces: number
  totalPrice: number
  bookingLimitDatetime: string
  priceDetail: string
}

const serializer = {
  startDatetime: (
    values: OfferEducationalStockFormValuesForSerializer,
    changedValues: CollectiveStockEditionBodyModel,
    departmentCode: string
  ) => ({
    ...changedValues,
    startDatetime: buildDatetimeForStockPayload(
      values.startDatetime,
      values.eventTime,
      departmentCode
    ),
  }),
  endDatetime: (
    values: OfferEducationalStockFormValuesForSerializer,
    changedValues: CollectiveStockEditionBodyModel,
    departmentCode: string
  ) => ({
    ...changedValues,
    endDatetime: buildDatetimeForStockPayload(
      values.endDatetime,
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
      values.startDatetime,
      values.eventTime,
      departmentCode
    ),
  }),
  numberOfPlaces: (
    values: OfferEducationalStockFormValuesForSerializer,
    changedValues: CollectiveStockEditionBodyModel
  ) => ({
    ...changedValues,
    numberOfTickets: values.numberOfPlaces,
  }),
  totalPrice: (
    values: OfferEducationalStockFormValuesForSerializer,
    changedValues: CollectiveStockEditionBodyModel
  ) => ({
    ...changedValues,
    totalPrice: values.totalPrice,
  }),
  bookingLimitDatetime: (
    values: OfferEducationalStockFormValuesForSerializer,
    changedValues: CollectiveStockEditionBodyModel,
    departmentCode: string
  ) => ({
    ...changedValues,
    bookingLimitDatetime: buildBookingLimitDatetimeForStockPayload(
      values.startDatetime,
      values.eventTime,
      values.bookingLimitDatetime,
      departmentCode
    ),
  }),
  priceDetail: (
    values: OfferEducationalStockFormValuesForSerializer,
    changedValues: CollectiveStockEditionBodyModel
  ) => ({
    ...changedValues,
    educationalPriceDetail: values.priceDetail,
  }),
}

const valuesIsOfferEducationalStockFormValuesForSerializer = (
  values: OfferEducationalStockFormValues
): values is OfferEducationalStockFormValuesForSerializer => {
  return (
    typeof values.numberOfPlaces === 'number' &&
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
