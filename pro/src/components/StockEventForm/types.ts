export interface IStockEventFormHiddenValues {
  stockId?: string
  isDeletable: boolean
  readOnlyFields: string[]
}

export interface IStockEventFormValues extends IStockEventFormHiddenValues {
  remainingQuantity: string
  bookingsQuantity: string
  quantity: number | '' | null
  bookingLimitDatetime: Date | null
  price: number | ''
  beginningDate: Date | '' | null
  beginningTime: Date | '' | null
}
