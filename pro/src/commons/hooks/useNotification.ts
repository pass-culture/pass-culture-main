/* istanbul ignore file */

import { useCallback, useMemo } from 'react'
import { useDispatch } from 'react-redux'

import { NOTIFICATION_SHOW_DURATION } from '@/commons/core/Notification/constants'
import {
  closeNotification,
  showNotification,
} from '@/commons/store/notifications/reducer'

export enum NotificationTypeEnum {
  SUCCESS = 'success',
  ERROR = 'error',
  INFORMATION = 'information',
}

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
      information: (msg: string | null, options: Options = {}) =>
        notify(msg, NotificationTypeEnum.INFORMATION, options),
      close: () => dispatch(closeNotification()),
    }),
    [dispatch, notify]
  )
}
