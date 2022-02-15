export type Stock = {
  activationCodesExpirationDatetime?: Date
  hasActivationCodes: boolean
  beginningDatetime?: Date
  bookingLimitDatetime?: Date
  dnBookedQuantity: number
  dateCreated: Date
  dateModified: Date
  id: string
  isEventDeletable: boolean
  isEventExpired: boolean
  offerId: string
  price: number
  quantity?: number
  numberOfTickets?: number
  isEducationalStockEditable?: boolean
  educationalPriceDetail?: string
}
