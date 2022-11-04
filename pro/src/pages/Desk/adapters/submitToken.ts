import { apiContremarque } from 'apiClient/api'
import { ApiError } from 'apiClient/v2'
import { IDeskSubmitResponse, MESSAGE_VARIANT } from 'screens/Desk'

const onSubmitFailure = (error: ApiError): IDeskSubmitResponse => ({
  error: {
    message: error.body['global'],
    variant: MESSAGE_VARIANT.ERROR,
  },
})

const submitValidate = (token: string): Promise<IDeskSubmitResponse> =>
  apiContremarque
    .patchBookingUseByToken(token)
    .then(() => ({}))
    .catch(onSubmitFailure)

const submitInvalidate = (token: string): Promise<IDeskSubmitResponse> =>
  apiContremarque
    .patchBookingKeepByToken(token)
    .then(() => ({}))
    .catch(onSubmitFailure)

export { submitValidate, submitInvalidate }
