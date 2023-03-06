export interface IStockEventFormHiddenValues {
  stockId?: string
  isDeletable: boolean
  readOnlyFields: string[]
}

export interface IStockEventFormValues extends IStockEventFormHiddenValues {
  bookingsQuantity: number
  remainingQuantity: number | ''
  bookingLimitDatetime: Date | null
  price: number | ''
  priceCategoryId: string | ''
  beginningDate: Date | '' | null
  beginningTime: Date | '' | null
}
