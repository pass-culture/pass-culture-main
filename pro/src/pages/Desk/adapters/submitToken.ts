import { apiContremarque } from 'apiClient/api'
import { isErrorAPIError } from 'apiClient/helpers'
import { ApiError } from 'apiClient/v2'

import { DeskSubmitResponse, MESSAGE_VARIANT } from '../types'

const onSubmitFailure = (error: ApiError): DeskSubmitResponse => ({
  error: {
    message: error.body['global'],
    variant: MESSAGE_VARIANT.ERROR,
  },
})

export const submitValidate = async (
  token: string
): Promise<DeskSubmitResponse> => {
  try {
    await apiContremarque.patchBookingUseByToken(token)
    return {}
  } catch (e) {
    if (!isErrorAPIError(e)) {
      return {}
    }
    return onSubmitFailure(e)
  }
}

export const submitInvalidate = async (
  token: string
): Promise<DeskSubmitResponse> => {
  try {
    await apiContremarque.patchBookingKeepByToken(token)
    return {}
  } catch (e) {
    if (!isErrorAPIError(e)) {
      return {}
    }
    return onSubmitFailure(e)
  }
}
