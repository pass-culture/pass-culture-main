/* istanbul ignore file */
import { useCallback, useMemo } from 'react'
import { useDispatch } from 'react-redux'

import { NOTIFICATION_SHOW_DURATION } from 'commons/core/Notification/constants'
import { type EnumType } from 'commons/custom_types/utils'
import {
  closeNotification,
  showNotification,
} from 'commons/store/notifications/reducer'

export const NotificationTypeEnum = {
  SUCCESS: 'success',
  ERROR: 'error',
  PENDING: 'pending',
  INFORMATION: 'information',
} as const
// eslint-disable-next-line no-redeclare
export type NotificationTypeEnum = EnumType<typeof NotificationTypeEnum>

interface Options {
  duration?: number
}

export const useNotification = () => {
  const dispatch = useDispatch()

  const notify = useCallback(
    (
      textMessage: string | null,
      type: NotificationTypeEnum,
      { duration = NOTIFICATION_SHOW_DURATION }: Options
    ) => {
      dispatch(
        showNotification({
          text: textMessage,
          type,
          duration,
        })
      )
    },
    [dispatch]
  )

  return useMemo(
    () => ({
      success: (msg: string | null, options: Options = {}) =>
        notify(msg, NotificationTypeEnum.SUCCESS, options),
      error: (msg: string | null, options: Options = {}) =>
        notify(msg, NotificationTypeEnum.ERROR, options),
      pending: (msg: string | null, options: Options = {}) =>
        notify(msg, NotificationTypeEnum.PENDING, options),
      information: (msg: string | null, options: Options = {}) =>
        notify(msg, NotificationTypeEnum.INFORMATION, options),
      close: () => dispatch(closeNotification()),
    }),
    [dispatch, notify]
  )
}
