import { captureException, withScope } from '@sentry/browser'
import type { Extras } from '@sentry/core/build/types/types-hoist/extra.d.ts'

import { NOTIFICATION_SHOW_DURATION } from 'commons/core/Notification/constants'
import { NotificationTypeEnum } from 'commons/hooks/useNotification'
import { showNotification } from 'commons/store/notifications/reducer'
import { rootStore } from 'commons/store/store'

import { FrontendError } from './FrontendError'

type HandleUnexpectedErrorOptions = Partial<{
  extras: Extras
  /**
   * Whether to notify the user about the error
   * @default false
   */
  isSilent: boolean
  /**
   * End-user message to display when `shouldNotifyUser` is true.
   * @default "Une erreur est survenue de notre côté. Veuillez réessayer plus tard."
   */
  userMessage: string
}>

const DEFAULT_OPTIONS: HandleUnexpectedErrorOptions = {
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
 *
 * @example
 * ```ts
 * const foundItem = items.find((item) => item.id === id)
 * if (!foundItem) {
 *   return handleUnexpectedError(new FrontendError('`foundItem` is undefined.'), {
 *     userMessage: 'Nous n’avons pas pu mettre à jour votre offre car une erreur est survenue. Veuillez réessayer plus tard.',
 *   })
 * }
 * ```
 */
export function handleUnexpectedError(
  error: FrontendError,
  options: HandleUnexpectedErrorOptions = {}
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
