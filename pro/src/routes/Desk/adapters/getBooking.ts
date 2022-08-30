import { apiContremarque } from 'apiClient/api'
import { HTTP_STATUS } from 'apiClient/helpers'
import { ApiError, GetBookingResponse } from 'apiClient/v2'
import {
  IBooking,
  IDeskGetBookingResponse,
  MESSAGE_VARIANT,
} from 'screens/Desk'

const getBookingSuccess = (
  response: GetBookingResponse
): IDeskGetBookingResponse => {
  return {
    booking: {
      datetime: response.datetime,
      ean13: response.ean13,
      offerName: response.offerName,
      price: response.price,
      quantity: response.quantity,
      userName: response.userName,
      venueDepartmentCode: response.venueDepartmentCode,
    } as IBooking,
  }
}

const getBookingFailure = (
  apiResponseError: ApiError
): IDeskGetBookingResponse => {
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
        variant: MESSAGE_VARIANT.DEFAULT,
      },
    }
  }
  if (apiResponseError.status === HTTP_STATUS.FORBIDDEN) {
    const apiReimbursedErrorMessage = apiResponseError.body['payment']
    if (apiReimbursedErrorMessage) {
      return {
        error: {
          isTokenValidated: false,
          message: apiReimbursedErrorMessage,
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

const getBooking = async (token: string): Promise<IDeskGetBookingResponse> => {
  return apiContremarque
    .getBookingByTokenV2(token)
    .then(getBookingSuccess)
    .catch(getBookingFailure)
}

export { getBooking }
