import { format } from 'date-fns'

import { GetOfferStockResponseModel } from 'apiClient/v1'
import { FORMAT_HH_mm, FORMAT_ISO_DATE_ONLY } from 'commons/utils/date'
import { getLocalDepartementDateTimeFromUtc } from 'commons/utils/timezone'
import { serializeDateTimeToUTCFromLocalDepartment } from 'components/IndividualOffer/StocksEventEdition/serializers'

import { EditStockFormValues } from './StocksCalendarTableEditStock'

export function getStockFormDefaultValues(
  stock: GetOfferStockResponseModel,
  departmentCode: string
) {
  return {
    date: stock.beginningDatetime
      ? format(
          getLocalDepartementDateTimeFromUtc(
            stock.beginningDatetime,
            departmentCode
          ),
          FORMAT_ISO_DATE_ONLY
        )
      : '',
    time: stock.beginningDatetime
      ? format(
          getLocalDepartementDateTimeFromUtc(
            stock.beginningDatetime,
            departmentCode
          ),
          FORMAT_HH_mm
        )
      : '',
    priceCategory: stock.priceCategoryId?.toString() || '',
    bookingLimitDate: stock.bookingLimitDatetime
      ? format(
          getLocalDepartementDateTimeFromUtc(
            stock.bookingLimitDatetime,
            departmentCode
          ),
          FORMAT_ISO_DATE_ONLY
        )
      : '',
    quantity:
      stock.quantity === null || stock.quantity === undefined
        ? undefined
        : stock.quantity,
  }
}

export function serializeStockFormValuesForUpdate(
  stockId: number,
  formValues: EditStockFormValues,
  departmentCode: string
) {
  const { priceCategory, quantity, date, time, bookingLimitDate } = formValues

  return {
    id: stockId,
    priceCategoryId: Number(priceCategory),
    quantity: quantity,
    beginningDatetime: serializeDateTimeToUTCFromLocalDepartment(
      format(date, FORMAT_ISO_DATE_ONLY),
      time,
      departmentCode
    ),
    bookingLimitDatetime: serializeDateTimeToUTCFromLocalDepartment(
      format(bookingLimitDate, FORMAT_ISO_DATE_ONLY),
      time,
      departmentCode
    ),
  }
}
