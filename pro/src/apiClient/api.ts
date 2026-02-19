import { client as adageClient } from './adage/client.gen'
import * as adageSdk from './adage/sdk.gen'
import { ApiError } from './compat'
import { client as v1Client } from './v1/client.gen'
import * as v1Sdk from './v1/sdk.gen'

function createApiErrorInterceptor() {
  return async (
    error: unknown,
    response: Response | undefined,
    request: Request
  ) =>
    new ApiError(
      request.url,
      response?.status ?? 0,
      response?.statusText ?? '',
      error
    )
}

v1Client.interceptors.error.use(createApiErrorInterceptor())
adageClient.interceptors.error.use(createApiErrorInterceptor())

export const api = v1Sdk
export const apiAdage = adageSdk

export {
  getDataFromAddress,
  getDataFromAddressParts,
} from '@/apiClient/adresse/apiAdresse'
