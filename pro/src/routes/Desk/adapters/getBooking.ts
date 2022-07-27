import { apiV2 } from 'api/api'
import {
  ApiError,
  HTTP_STATUS,
  extractApiErrorMessageForKey,
  extractApiFirstErrorMessage,
} from 'api/helpers'
import { GetBookingResponse } from 'api/v2/gen'
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
  const errorMessage = extractApiFirstErrorMessage(apiResponseError)
  if (apiResponseError.statusCode === HTTP_STATUS.GONE) {
    // api return HTTP_STATUS.GONE when :
    // * booking is already been validated
    // * booking is already been canceled
    const apiCancelledErrorMessage = extractApiErrorMessageForKey(
      apiResponseError,
      'booking_cancelled'
    )
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
  return {
    error: {
      isTokenValidated: false,
      message: errorMessage,
      variant: MESSAGE_VARIANT.ERROR,
    },
  }
}

const getBooking = (token: string): Promise<IDeskGetBookingResponse> => {
  return apiV2
    .getBookingsGetBookingByTokenV2(token)
    .then(getBookingSuccess)
    .catch(getBookingFailure)
}

export { getBooking }
