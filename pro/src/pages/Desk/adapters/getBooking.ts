import { apiContremarque } from 'apiClient/api'
import { HTTP_STATUS, isErrorAPIError } from 'apiClient/helpers'
import { ApiError } from 'apiClient/v2'

import { DeskGetBookingResponse, MESSAGE_VARIANT } from '../types'

const getBookingFailure = (
  apiResponseError: ApiError
): DeskGetBookingResponse => {
  const errorMessage = apiResponseError.message
  if (apiResponseError.status === HTTP_STATUS.GONE) {
    // api return HTTP_STATUS.GONE when :
    // * booking is already been validated
    // * booking is already been canceled
    const apiCancelledErrorMessage = apiResponseError.body['booking_cancelled']

    if (apiCancelledErrorMessage) {
      return {
        error: {
          isTokenValidated: false,
          message: apiCancelledErrorMessage,
          variant: MESSAGE_VARIANT.ERROR,
        },
      }
    }

    return {
      error: {
        // api return HTTP_STATUS.GONE when booking is already been validated
        isTokenValidated: true,
        message: errorMessage,
        variant: MESSAGE_VARIANT.ERROR,
      },
    }
  }
  if (apiResponseError.status === HTTP_STATUS.FORBIDDEN) {
    const apiReimbursedErrorMessage = apiResponseError.body['payment']
    const apiCantBeValidatedErrorMessage = apiResponseError.body['booking']
    if (apiReimbursedErrorMessage) {
      return {
        error: {
          isTokenValidated: false,
          message: apiReimbursedErrorMessage,
          variant: MESSAGE_VARIANT.ERROR,
        },
      }
    }
    if (apiCantBeValidatedErrorMessage) {
      return {
        error: {
          isTokenValidated: false,
          message: apiCantBeValidatedErrorMessage,
          variant: MESSAGE_VARIANT.ERROR,
        },
      }
    }
  }
  return {
    error: {
      isTokenValidated: false,
      message: errorMessage,
      variant: MESSAGE_VARIANT.ERROR,
    },
  }
}

export const getBooking = async (
  token: string
): Promise<DeskGetBookingResponse> => {
  try {
    const response = await apiContremarque.getBookingByTokenV2(token)
    return { booking: response }
  } catch (e) {
    if (!isErrorAPIError(e)) {
      return {}
    }
    return getBookingFailure(e)
  }
}
