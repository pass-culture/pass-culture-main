import endOfDay from 'date-fns/endOfDay'

import { StockCreationBodyModel, StockEditionBodyModel } from 'apiClient/v1'
import { IStockThingFormValues } from 'components/StockThingForm'
import { toISOStringWithoutMilliseconds } from 'utils/date'
import { getUtcDateTimeFromLocalDepartement } from 'utils/timezone'

const serializeThingBookingLimitDatetime = (
  bookingLimitDatetime: Date,
  departementCode: string
) => {
  const endOfBookingLimitDayUtcDatetime = getUtcDateTimeFromLocalDepartement(
    endOfDay(bookingLimitDatetime),
    departementCode
  )
  return toISOStringWithoutMilliseconds(endOfBookingLimitDayUtcDatetime)
}

export const serializeStockThingList = (
  formValues: IStockThingFormValues,
  departementCode: string
): StockCreationBodyModel[] | StockEditionBodyModel[] => {
  const apiStock: StockCreationBodyModel = {
    bookingLimitDatetime: formValues.bookingLimitDatetime
      ? serializeThingBookingLimitDatetime(
          formValues.bookingLimitDatetime,
          departementCode
        )
      : null,
    price: parseInt(formValues.price, 10),
    quantity: parseInt(formValues.quantity, 10) || null,
  }
  if (formValues.activationCodes.length > 0) {
    apiStock.activationCodes = formValues.activationCodes
    if (formValues.activationCodesExpirationDateTime)
      apiStock.activationCodesExpirationDatetime =
        serializeThingBookingLimitDatetime(
          formValues.activationCodesExpirationDateTime,
          departementCode
        )
  }
  if (formValues.stockId) {
    return [
      {
        ...apiStock,
        humanizedId: formValues.stockId,
      },
    ]
  }
  return [apiStock]
}
