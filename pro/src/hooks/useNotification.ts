/* istanbul ignore file: RomainC, I think testing is ok with this file*/
import { useMemo } from 'react'
import { useDispatch } from 'react-redux'

import { NOTIFICATION_SHOW_DURATION } from 'core/Notification/constants'
import {
  closeNotification,
  showNotification,
} from 'store/notifications/reducer'

export enum NotificationTypeEnum {
  SUCCESS = 'success',
  ERROR = 'error',
  PENDING = 'pending',
  INFORMATION = 'information',
}

interface Options {
  duration?: number
}

export const useNotification = () => {
  const dispatch = useDispatch()
  const notify = (
    textMessage: string | null,
    type: NotificationTypeEnum,
    { duration = NOTIFICATION_SHOW_DURATION }: Options
  ) => {
    dispatch(
      showNotification({
        text: textMessage,
        type: type,
        duration,
      })
    )
  }

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
    [dispatch]
  )
}
