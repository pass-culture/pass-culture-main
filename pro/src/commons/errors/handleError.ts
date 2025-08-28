import { captureException, withScope } from '@sentry/browser'
import { NOTIFICATION_SHOW_DURATION } from 'commons/core/Notification/constants'
import { NotificationTypeEnum } from 'commons/hooks/useNotification'
import { showNotification } from 'commons/store/notifications/reducer'
import { rootStore } from 'commons/store/store'

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
    showNotification({
      text: userMessage,
      type: NotificationTypeEnum.ERROR,
      duration: NOTIFICATION_SHOW_DURATION,
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
