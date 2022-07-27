import { apiV2 } from 'api/api'
import { ApiError, extractApiErrorMessageForKey } from 'api/helpers'
import { IDeskSubmitResponse, MESSAGE_VARIANT } from 'screens/Desk'

const onSubmitFailure = (error: ApiError): IDeskSubmitResponse => ({
  error: {
    message: extractApiErrorMessageForKey(error, 'global'),
    variant: MESSAGE_VARIANT.ERROR,
  },
})

const submitValidate = (token: string): Promise<IDeskSubmitResponse> =>
  apiV2
    .patchBookingsPatchBookingUseByToken(token)
    .then(() => ({}))
    .catch(onSubmitFailure)

const submitInvalidate = (token: string): Promise<IDeskSubmitResponse> =>
  apiV2
    .patchBookingsPatchBookingKeepByToken(token)
    .then(() => ({}))
    .catch(onSubmitFailure)

export { submitValidate, submitInvalidate }
