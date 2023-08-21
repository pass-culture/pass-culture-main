import { GetBookingResponse } from 'apiClient/v2'

export enum MESSAGE_VARIANT {
  DEFAULT = 'default',
  ERROR = 'error',
}

export interface ErrorMessage {
  message: string
  variant: MESSAGE_VARIANT
}

export interface DeskGetBookingResponse {
  error?: ErrorMessage & {
    isTokenValidated: boolean
  }
  booking?: GetBookingResponse
}

export interface DeskProps {
  getBooking: (token: string) => Promise<DeskGetBookingResponse>
  submitInvalidate: (token: string) => Promise<DeskSubmitResponse>
  submitValidate: (token: string) => Promise<DeskSubmitResponse>
}

export interface DeskSubmitResponse {
  error?: ErrorMessage
}
