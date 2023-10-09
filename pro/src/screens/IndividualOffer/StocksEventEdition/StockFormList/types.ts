import { useFormik } from 'formik'

export interface StockEventFormHiddenValues {
  stockId?: number
  isDeletable: boolean
  readOnlyFields: string[]
}

export interface StockEventFormValues extends StockEventFormHiddenValues {
  bookingsQuantity: number
  remainingQuantity: number | ''
  bookingLimitDatetime: string
  priceCategoryId: string | ''
  beginningDate: string
  beginningTime: string
}

export interface StocksEventFormValues {
  stocks: StockEventFormValues[]
}

export type StocksEventFormik = ReturnType<
  typeof useFormik<StocksEventFormValues>
>
