import { captureException, withScope } from '@sentry/browser'
import { addSnackBar } from 'commons/store/snackBar/reducer'
import { rootStore } from 'commons/store/store'

import { SnackBarVariant } from '@/design-system/SnackBar/SnackBar'

import type { FrontendErrorOptions } from './types'

/**
 * Gracefully handles any caught error by:
 * - Notifying the user
 * - Logging it to Sentry
 * - Logging it to the console
 *
 * Can be used anywhere, inluding outside of the Redux context.
 */
export function handleError(
  error: unknown,
  userMessage: string,
  options: Omit<FrontendErrorOptions, 'isSilent' | 'userMessage'> = {}
): void {
  const { extras } = options

  rootStore.dispatch(
    addSnackBar({
      description: userMessage,
      variant: SnackBarVariant.ERROR,
    })
  )

  withScope((scope) => {
    if (extras) {
      scope.setExtras(extras)
    }

    captureException(error)
  })

  console.error(error)
}
