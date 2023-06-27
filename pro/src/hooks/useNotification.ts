/* istanbul ignore file: RomainC, I think testing is ok with this file*/
import { useCallback, useMemo } from 'react'
import { useDispatch } from 'react-redux'

import { NOTIFICATION_SHOW_DURATION } from 'core/Notification/constants'
import {
  closeNotification,
  showNotification,
} from 'store/reducers/notificationReducer'

export enum NotificationTypeEnum {
  SUCCESS = 'success',
  ERROR = 'error',
  PENDING = 'pending',
  INFORMATION = 'information',
}

interface Options {
  duration?: number
}

const useNotification = () => {
  const dispatch = useDispatch()
  const dispatchNotification = useCallback(
    (
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
    },
    [dispatch]
  )
  const dispatchCloseNotification = useCallback(
    () => dispatch(closeNotification()),
    [dispatch]
  )

  return useMemo(
    () => ({
      success: (msg: string | null, options: Options = {}) =>
        dispatchNotification(msg, NotificationTypeEnum.SUCCESS, options),
      error: (msg: string | null, options: Options = {}) =>
        dispatchNotification(msg, NotificationTypeEnum.ERROR, options),
      pending: (msg: string | null, options: Options = {}) =>
        dispatchNotification(msg, NotificationTypeEnum.PENDING, options),
      information: (msg: string | null, options: Options = {}) =>
        dispatchNotification(msg, NotificationTypeEnum.INFORMATION, options),
      close: () => dispatchCloseNotification(),
    }),
    [dispatchCloseNotification, dispatchNotification]
  )
}

export default useNotification
