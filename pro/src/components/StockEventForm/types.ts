export interface IStockEventFormHiddenValues {
  stockId?: string
  isDeletable: boolean
  readOnlyFields: string[]
}

export interface IStockEventFormValues extends IStockEventFormHiddenValues {
  remainingQuantity: string
  bookingsQuantity: string
  quantity: string
  bookingLimitDatetime: Date | null
  price: string
  beginningDate: Date | '' | null
  beginningTime: Date | '' | null
}
