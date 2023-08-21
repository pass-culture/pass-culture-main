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

export interface DeskSubmitResponse {
  error?: ErrorMessage
}
