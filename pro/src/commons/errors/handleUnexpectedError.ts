import { captureException, withScope } from '@sentry/browser'

import { NOTIFICATION_SHOW_DURATION } from 'commons/core/Notification/constants'
import { NotificationTypeEnum } from 'commons/hooks/useNotification'
import { showNotification } from 'commons/store/notifications/reducer'
import { rootStore } from 'commons/store/store'

import { FrontendError } from './FrontendError'
import { FrontendErrorOptions } from './types'

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
  const { extras, isSilent, userMessage } = {
    ...DEFAULT_OPTIONS,
    ...options,
  }

  if (!isSilent && typeof userMessage === 'string') {
    rootStore.dispatch(
      showNotification({
        text: userMessage,
        type: NotificationTypeEnum.ERROR,
        duration: NOTIFICATION_SHOW_DURATION,
      })
    )
  }

  withScope((scope) => {
    if (extras) {
      scope.setExtras(extras)
    }

    captureException(error)
  })

  // eslint-disable-next-line no-console
  console.error(error)
}
