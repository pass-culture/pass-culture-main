export enum MESSAGE_VARIANT {
  DEFAULT = 'default',
  ERROR = 'error',
}

export interface IErrorMessage {
  message: string
  variant: MESSAGE_VARIANT
}

export interface IBooking {
  datetime: string
  ean13?: string | null
  offerName: string
  price: number
  quantity: number
  userName: string
  venueDepartmentCode?: string | null
}

export interface IDeskGetBookingResponse {
  error?: IErrorMessage & {
    isTokenValidated: boolean
  }
  booking?: IBooking
}

export interface IDeskProps {
  getBooking: (token: string) => Promise<IDeskGetBookingResponse>
  submitInvalidate: (token: string) => Promise<IDeskSubmitResponse>
  submitValidate: (token: string) => Promise<IDeskSubmitResponse>
}

export interface IDeskSubmitResponse {
  error?: IErrorMessage
}
