/* istanbul ignore file */
import { useCallback, useMemo } from 'react'
import { useDispatch } from 'react-redux'

import { NOTIFICATION_SHOW_DURATION } from 'core/Notification/constants'
import {
  closeNotification,
  showNotification,
} from 'store/reducers/notificationReducer'

enum TypeEnum {
  SUCCESS = 'success',
  ERROR = 'error',
  PENDING = 'pending',
  INFORMATION = 'information',
}

interface IOptions {
  duration?: number
  withStickyActionBar?: boolean
}

const useNotification = () => {
  const dispatch = useDispatch()
  const dispatchNotification = useCallback(
    (
      textMessage: string | null,
      type: TypeEnum,
      {
        duration = NOTIFICATION_SHOW_DURATION,
        withStickyActionBar = false,
      }: IOptions
    ) => {
      dispatch(
        showNotification({
          text: textMessage,
          type: type,
          duration,
          withStickyActionBar,
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
      success: (msg: string | null, options: IOptions = {}) =>
        dispatchNotification(msg, TypeEnum.SUCCESS, options),
      error: (msg: string | null, options: IOptions = {}) =>
        dispatchNotification(msg, TypeEnum.ERROR, options),
      pending: (msg: string | null, options: IOptions = {}) =>
        dispatchNotification(msg, TypeEnum.PENDING, options),
      information: (msg: string | null, options: IOptions = {}) =>
        dispatchNotification(msg, TypeEnum.INFORMATION, options),
      close: () => dispatchCloseNotification(),
    }),
    [dispatchCloseNotification, dispatchNotification]
  )
}

export default useNotification
