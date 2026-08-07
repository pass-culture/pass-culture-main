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

// biome-ignore lint/suspicious/noExplicitAny: the generated SDK signatures are restored by the cast in `withCallSites`
type AsyncFn = (...args: any[]) => Promise<unknown>

/**
 * Records where an API call was made from, so the information survives to Sentry.
 *
 * Once the request is awaited, the caller's frames are gone: Firefox only
 * reconstructs async frames when DevTools is attached (the
 * `javascript.options.asyncstack_capture_debuggee_only` pref, on by default),
 * so in the field an ApiError's own stack stops at the first `await` inside the
 * generated client — three frames, identical for every endpoint.
 *
 * Building the Error on entry, before any await, captures the caller's real
 * stack synchronously, which every engine reports. It is attached as `cause` so
 * that Sentry's linkedErrors integration reports it as a chained exception.
 */
function withCallSite<T extends AsyncFn>(fn: T, name: string): T {
  return ((...args: Parameters<T>) => {
    const callSite = new Error(`api.${name}()`)
    callSite.name = 'ApiCallSite'

    return fn(...args).catch((error: unknown) => {
      // `cause` is ES2022 and this project targets es2021, hence the cast.
      const withCause = error as { cause?: unknown }
      if (error instanceof Error && withCause.cause === undefined) {
        withCause.cause = callSite
      }
      throw error
    })
  }) as T
}

function withCallSites<T extends object>(sdk: T): T {
  return Object.fromEntries(
    Object.entries(sdk).map(([name, value]) => [
      name,
      typeof value === 'function'
        ? withCallSite(value as AsyncFn, name)
        : value,
    ])
  ) as T
}

/**
 * Plain object wrapper around the generated v1 SDK so consumers can spy on it via `vi.spyOn(api, '...')`.
 * ES module namespace objects are frozen which prevents spying on them directly.
 */
// Careful here:
// The originally frozen ES module namespace objects prevented any accidental mutation, which we lose with this spread.
export const api = withCallSites({ ...v1Sdk })
export const apiAdage = withCallSites({ ...adageSdk })
