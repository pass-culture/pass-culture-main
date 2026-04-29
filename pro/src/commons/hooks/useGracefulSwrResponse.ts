import { useEffect, useRef } from 'react'
import type { SWRResponse } from 'swr'

import { assertOrFrontendError } from '../errors/assertOrFrontendError'
import { useSnackBar } from './useSnackBar'

interface UseGracefulSwrResponse<Data> {
  data: Data | undefined
  hasFirstLoadError: boolean
  hasReloadError: boolean
  isFirstLoading: boolean
  isReloading: boolean
}

interface FirstLoadingResponse<Data> extends UseGracefulSwrResponse<Data> {
  data: undefined
  hasFirstLoadError: false
  hasReloadError: false
  isFirstLoading: true
  isReloading: false
}
interface ReloadingResponse<Data> extends UseGracefulSwrResponse<Data> {
  data: Data
  hasFirstLoadError: false
  hasReloadError: false
  isFirstLoading: false
  isReloading: true
}
interface SuccessfulResponse<Data> extends UseGracefulSwrResponse<Data> {
  data: Data
  hasFirstLoadError: false
  hasReloadError: false
  isFirstLoading: false
  isReloading: false
}
interface FailedResponseOnFirstLoad<Data> extends UseGracefulSwrResponse<Data> {
  data: undefined
  hasFirstLoadError: true
  hasReloadError: false
  isFirstLoading: false
  isReloading: false
}
interface FailedResponseOnReload<Data> extends UseGracefulSwrResponse<Data> {
  data: Data
  hasFirstLoadError: false
  hasReloadError: true
  isFirstLoading: false
  isReloading: false
}

/**
 * - Gracefully handle SWR query errors in a normalized way.
 * - Guarantee that `data` is always defined once `isFirstLoading` is false.
 * - Falls back to the last known data in case of reload error.
 *
 * @example
 * ```tsx
 * const swrResponse = useSWR(...)
 * const { data, hasFirstLoadError, isFirstLoading } = useGracefulSwrResponse(
 *   swrResponse,
 *   'Une erreur est survenue pendant le rafraîchissement des offres.'
 * )
 * if (isFirstLoading) {
 *   return <Spinner />
 * }
 * if (hasFirstLoadError) {
 *   return <p>Nous n'avons pas pu récupérer la liste des offres.</p>
 * }
 *
 * // At this point `data` is guaranteed to be defined.
 * ```
 */
export function useGracefulSwrResponse<Data>(
  swrResponse: SWRResponse<Data>,
  userErrorMessageOnReload: string
):
  | FirstLoadingResponse<Data>
  | ReloadingResponse<Data>
  | SuccessfulResponse<Data>
  | FailedResponseOnFirstLoad<Data>
  | FailedResponseOnReload<Data> {
  const lastDataRef = useRef<Data | undefined>(undefined)
  // Updating refs and states on props changes during rendering is OK as long the render stays pure:
  // https://react.dev/learn/you-might-not-need-an-effect#adjusting-some-state-when-a-prop-changes
  if (swrResponse.data !== undefined) {
    lastDataRef.current = swrResponse.data
  }

  const snackbar = useSnackBar()

  useEffect(() => {
    if (swrResponse.error && lastDataRef.current !== undefined) {
      snackbar.error(userErrorMessageOnReload)
    }
  }, [swrResponse.error, snackbar.error, userErrorMessageOnReload])

  if (swrResponse.isLoading) {
    return {
      data: undefined,
      hasFirstLoadError: false,
      hasReloadError: false,
      isFirstLoading: true,
      isReloading: false,
    } satisfies FirstLoadingResponse<Data>
  }

  if (lastDataRef.current === undefined && swrResponse.error) {
    return {
      data: undefined,
      hasFirstLoadError: true,
      hasReloadError: false,
      isFirstLoading: false,
      isReloading: false,
    } satisfies FailedResponseOnFirstLoad<Data>
  }

  assertOrFrontendError(
    lastDataRef.current,
    '`lastDataRef.current` is undefined.'
  )

  if (swrResponse.isValidating) {
    return {
      data: lastDataRef.current,
      hasFirstLoadError: false,
      hasReloadError: false,
      isFirstLoading: false,
      isReloading: true,
    } satisfies ReloadingResponse<Data>
  }

  return {
    data: lastDataRef.current,
    hasFirstLoadError: false,
    hasReloadError: !!swrResponse.error,
    isFirstLoading: false,
    isReloading: false,
  } satisfies SuccessfulResponse<Data> | FailedResponseOnReload<Data>
}
