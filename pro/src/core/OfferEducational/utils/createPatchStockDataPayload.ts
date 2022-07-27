import isEqual from 'lodash.isequal'

import { CollectiveStockEditionBodyModel } from 'apiClient/v1'

import { OfferEducationalStockFormValues } from '../types'

import {
  buildBeginningDatetimeForStockPayload,
  buildBookingLimitDatetimeForStockPayload,
} from './buildDatetimesForStockPayload'

type OfferEducationalStockFormValuesForSerializer = {
  eventDate: Date
  eventTime: Date
  numberOfPlaces: number
  totalPrice: number
  bookingLimitDatetime: Date | null
  priceDetail: string
}

const serializer = {
  eventDate: (
    values: OfferEducationalStockFormValuesForSerializer,
    changedValues: CollectiveStockEditionBodyModel,
    departmentCode: string
  ) => ({
    ...changedValues,
    beginningDatetime: buildBeginningDatetimeForStockPayload(
      values.eventDate,
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
    beginningDatetime: buildBeginningDatetimeForStockPayload(
      values.eventDate,
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
      values.eventDate,
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
  values: Omit<OfferEducationalStockFormValues, 'educationalOfferType'>
): values is OfferEducationalStockFormValuesForSerializer => {
  return (
    values.eventDate !== null &&
    values.eventTime !== null &&
    typeof values.numberOfPlaces === 'number' &&
    typeof values.totalPrice === 'number'
  )
}

const getValuesWithoutEducationalOfferTypeAttribute = (
  values: OfferEducationalStockFormValues
): Omit<OfferEducationalStockFormValues, 'educationalOfferType'> => {
  return (
    Object.keys(values) as (keyof OfferEducationalStockFormValues)[]
  ).reduce((result, valueKey) => {
    if (valueKey === 'educationalOfferType') {
      return result
    }
    return {
      ...result,
      [valueKey]: values[valueKey],
    }
  }, {} as Omit<OfferEducationalStockFormValues, 'educationalOfferType'>)
}

export const createPatchStockDataPayload = (
  values: OfferEducationalStockFormValues,
  departmentCode: string,
  initialValues: OfferEducationalStockFormValues
): CollectiveStockEditionBodyModel => {
  let changedValues: CollectiveStockEditionBodyModel = {}

  const valuesWithoutEducationalOfferType =
    getValuesWithoutEducationalOfferTypeAttribute(values)

  const stockKeys = Object.keys(initialValues).filter(
    key => key !== 'educationalOfferType'
  ) as (keyof Omit<OfferEducationalStockFormValues, 'educationalOfferType'>)[]

  if (
    valuesIsOfferEducationalStockFormValuesForSerializer(
      valuesWithoutEducationalOfferType
    )
  ) {
    stockKeys.forEach(key => {
      if (
        !isEqual(valuesWithoutEducationalOfferType[key], initialValues[key])
      ) {
        changedValues = serializer[key](
          valuesWithoutEducationalOfferType,
          changedValues,
          departmentCode
        )
      }
    })
  }

  return changedValues
}
