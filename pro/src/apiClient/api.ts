import { withCallSites } from '@/apiClient/callSite'
import { ApiError, normalizeApiPath } from '@/apiClient/compat'

import { client as adageClient } from './adage/client.gen'
import { client as v1Client } from './v1/client.gen'

function createApiErrorInterceptor() {
  return async (
    error: unknown,
    response: Response | undefined,
    request: Request | undefined
  ) =>
    response?.status && request
      ? new ApiError(
          request.url,
          response.status,
          response.statusText,
          error,
          `${request.method} ${normalizeApiPath(request.url)}`
        )
      : error
}

v1Client.interceptors.error.use(createApiErrorInterceptor())
adageClient.interceptors.error.use(createApiErrorInterceptor())

import * as adageSdk from '@/apiClient/adage/sdk.gen'
import * as v1Sdk from '@/apiClient/v1/sdk.gen'

export {
  getDataFromAddress,
  getDataFromAddressParts,
} from '@/apiClient/adresse/apiAdresse'

/**
 * Plain object wrappers around the generated SDKs:
 *  - Recording call sites (see `withCallSites`)
 *  - Spreading the module namespace so consumers can spy on these via `vi.spyOn(api, '...')`.
 */
// Careful here:
// The originally frozen ES module namespace objects prevented any accidental mutation, which we lose with this spread.
export const api = withCallSites({ ...v1Sdk })
export const apiAdage = withCallSites({ ...adageSdk })
