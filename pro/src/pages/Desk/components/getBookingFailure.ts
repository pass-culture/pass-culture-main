import type { ApiError } from '@/apiClient/compat'
import { HTTP_STATUS } from '@/apiClient/helpers'

type DeskGetFailure = {
  isTokenValidated: boolean
  message: string
}

const errors: Record<number, string> = {
  401: 'Authentification nécessaire',
  404: "La contremarque n'existe pas, ou vous n'avez pas les droits nécessaires pour y accéder.",
  410: "Cette contremarque a été validée. En l'invalidant vous indiquez qu'elle n'a pas été utilisée et vous ne serez pas remboursé.",
  422: 'Unprocessable Content',
}

export const getBookingFailure = (
  apiResponseError: ApiError
): DeskGetFailure => {
  const errorMessage = errors[apiResponseError.status]
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
