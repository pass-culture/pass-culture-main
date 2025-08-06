import { HTTP_STATUS } from '@/apiClient/helpers'
import { ApiError } from '@/apiClient/v1'

type DeskGetFailure = {
  isTokenValidated: boolean
  message: string
}

export const getBookingFailure = (
  apiResponseError: ApiError
): DeskGetFailure => {
  const errorMessage = apiResponseError.message
  if (apiResponseError.status === HTTP_STATUS.GONE) {
    // api return HTTP_STATUS.GONE when :
    // * booking is already been validated
    // * booking is already been canceled
    const apiCancelledErrorMessage = apiResponseError.body['booking_cancelled']

    if (apiCancelledErrorMessage) {
      return {
        isTokenValidated: false,
        message: apiCancelledErrorMessage,
      }
    }

    return {
      // api return HTTP_STATUS.GONE when booking is already been validated
      isTokenValidated: true,
      message: errorMessage,
    }
  }
  if (apiResponseError.status === HTTP_STATUS.FORBIDDEN) {
    const apiReimbursedErrorMessage = apiResponseError.body['payment']
    const apiCantBeValidatedErrorMessage = apiResponseError.body['booking']
    if (apiReimbursedErrorMessage) {
      return {
        isTokenValidated: false,
        message: apiReimbursedErrorMessage,
      }
    }
    if (apiCantBeValidatedErrorMessage) {
      return {
        isTokenValidated: false,
        message: apiCantBeValidatedErrorMessage,
      }
    }
  }

  return {
    isTokenValidated: false,
    message: errorMessage,
  }
}
