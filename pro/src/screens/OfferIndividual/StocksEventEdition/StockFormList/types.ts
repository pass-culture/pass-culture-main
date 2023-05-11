export interface IStockEventFormHiddenValues {
  stockId?: number
  isDeletable: boolean
  readOnlyFields: string[]
}

export interface IStockEventFormValues extends IStockEventFormHiddenValues {
  bookingsQuantity: number
  remainingQuantity: number | ''
  bookingLimitDatetime: Date | null
  priceCategoryId: string | ''
  beginningDate: Date | '' | null
  beginningTime: Date | '' | null
}
