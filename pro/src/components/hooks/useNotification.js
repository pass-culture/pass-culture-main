import { useCallback, useMemo } from 'react'
import { useDispatch } from 'react-redux'

import { NOTIFICATION_SHOW_DURATION } from 'core/Notification/constants'
import {
  closeNotification,
  showNotification,
} from 'store/reducers/notificationReducer'

const useNotification = () => {
  const dispatch = useDispatch()
  const dispatchNotification = useCallback(
    (textMessage, duration = NOTIFICATION_SHOW_DURATION, type) => {
      dispatch(
        showNotification({
          text: textMessage,
          duration,
          type: type,
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
      success: (msg, duration) =>
        dispatchNotification(msg, duration, 'success'),
      error: (msg, duration) => dispatchNotification(msg, duration, 'error'),
      pending: (msg, duration) =>
        dispatchNotification(msg, duration, 'pending'),
      information: (msg, duration) =>
        dispatchNotification(msg, duration, 'information'),
      close: () => dispatchCloseNotification(),
    }),
    [dispatchCloseNotification, dispatchNotification]
  )
}

export default useNotification
