import { ApiError } from '@/apiClient/compat'

import { client as adageClient } from './adage/new/client.gen'
import { client as v1Client } from './v1/new/client.gen'

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

import * as v1NewSdk from '@/apiClient/v1/new/sdk.gen'

export * as apiAdageNew from '@/apiClient/adage/new/sdk.gen'
export {
  getDataFromAddress,
  getDataFromAddressParts,
} from '@/apiClient/adresse/apiAdresse'

/**
 * Plain object wrapper around the generated v1 SDK so consumers can spy on it via `vi.spyOn(apiNew, '...')`.
 * ES module namespace objects are frozen which prevents spying on them directly.
 */
// Careful here:
// The originally frozen ES module namespace objects prevented any accidental mutation, which we lose with this spread.
export const apiNew = { ...v1NewSdk }
