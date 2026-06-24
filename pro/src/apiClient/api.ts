import { ApiError } from '@/apiClient/compat'

import { client as adageClient } from './adage/client.gen'
import { client as v1Client } from './v1/client.gen'

function createApiErrorInterceptor() {
  return async (
    error: unknown,
    response: Response | undefined,
    request: Request
  ) =>
    response?.status
      ? new ApiError(
          request.url,
          response.status,
          response.statusText ?? '',
          error
        )
      : error
}

v1Client.interceptors.error.use(createApiErrorInterceptor())
adageClient.interceptors.error.use(createApiErrorInterceptor())

import * as v1Sdk from '@/apiClient/v1/sdk.gen'

export * as apiAdage from '@/apiClient/adage/sdk.gen'
export {
  getDataFromAddress,
  getDataFromAddressParts,
} from '@/apiClient/adresse/apiAdresse'

/**
 * Plain object wrapper around the generated v1 SDK so consumers can spy on it via `vi.spyOn(api, '...')`.
 * ES module namespace objects are frozen which prevents spying on them directly.
 */
// Careful here:
// The originally frozen ES module namespace objects prevented any accidental mutation, which we lose with this spread.
export const api = { ...v1Sdk }
