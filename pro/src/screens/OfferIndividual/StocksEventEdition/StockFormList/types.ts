export interface StockEventFormHiddenValues {
  stockId?: number
  isDeletable: boolean
  readOnlyFields: string[]
}

export interface StockEventFormValues extends StockEventFormHiddenValues {
  bookingsQuantity: number
  remainingQuantity: number | ''
  bookingLimitDatetime: Date | null
  priceCategoryId: string | ''
  beginningDate: Date | '' | null
  beginningTime: Date | '' | null
}
