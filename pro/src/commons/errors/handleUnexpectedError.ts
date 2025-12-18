import { captureException, withScope } from '@sentry/browser'
import { addSnackBar } from 'commons/store/snackBar/reducer'
import { rootStore } from 'commons/store/store'

import { SnackBarVariant } from '@/design-system/SnackBar/SnackBar'

import type { FrontendError } from './FrontendError'
import type { FrontendErrorOptions } from './types'

const DEFAULT_OPTIONS: FrontendErrorOptions = {
  isSilent: false,
  userMessage:
    'Une erreur est survenue de notre côté. Veuillez réessayer plus tard.',
}

/**
 * Gracefully handles an unexpected error (= "that should never happen") by:
 * - Notifying the user (unless `isSilent` is true)
 * - Logging it to Sentry
 * - Logging it to the console
 *
 * Can be used anywhere, inluding outside of the Redux context.
 */
export function handleUnexpectedError(
  error: FrontendError,
  options: FrontendErrorOptions = {}
): void {
  const { context, extras, isSilent, userMessage } = {
    ...DEFAULT_OPTIONS,
    ...options,
  }

  if (!isSilent && typeof userMessage === 'string') {
    rootStore.dispatch(
      addSnackBar({
        text: userMessage,
        variant: SnackBarVariant.ERROR,
      })
    )
  }

  withScope((scope) => {
    if (context) {
      scope.setContext('context', context)
    }

    if (extras) {
      scope.setExtras(extras)
    }

    captureException(error)
  })

  console.error(error)
}
