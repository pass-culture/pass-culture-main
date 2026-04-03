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
  const { context } = options

  const isUserImpersonated: boolean | null =
    rootStore.getState().user.currentUser?.isImpersonated ?? null

  rootStore.dispatch(
    addSnackBar({
      description: userMessage,
      variant: SnackBarVariant.ERROR,
    })
  )

  withScope((scope) => {
    scope.setContext('default', {
      isUserImpersonated,
    })
    if (context) {
      scope.setContext('custom', context)
    }

    captureException(error)
  })

  console.error(error)
}
