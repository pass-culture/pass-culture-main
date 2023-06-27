export enum MESSAGE_VARIANT {
  DEFAULT = 'default',
  ERROR = 'error',
}

export interface ErrorMessage {
  message: string
  variant: MESSAGE_VARIANT
}

export interface Booking {
  datetime: string
  ean13?: string | null
  offerName: string
  price: number
  quantity: number
  userName: string
  priceCategoryLabel: string | null
  venueDepartmentCode?: string | null
}

export interface DeskGetBookingResponse {
  error?: ErrorMessage & {
    isTokenValidated: boolean
  }
  booking?: Booking
}

export interface DeskProps {
  getBooking: (token: string) => Promise<DeskGetBookingResponse>
  submitInvalidate: (token: string) => Promise<DeskSubmitResponse>
  submitValidate: (token: string) => Promise<DeskSubmitResponse>
}

export interface DeskSubmitResponse {
  error?: ErrorMessage
}
