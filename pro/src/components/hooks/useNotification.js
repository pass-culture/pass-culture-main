/* istanbul ignore file */
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
    (
      textMessage,
      duration = NOTIFICATION_SHOW_DURATION,
      withStickyActionBar = false,
      type
    ) => {
      dispatch(
        showNotification({
          text: textMessage,
          duration,
          withStickyActionBar,
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
      success: (msg, duration, withStickyActionBar) =>
        dispatchNotification(msg, duration, withStickyActionBar, 'success'),
      error: (msg, duration, withStickyActionBar) =>
        dispatchNotification(msg, duration, withStickyActionBar, 'error'),
      pending: (msg, duration, withStickyActionBar) =>
        dispatchNotification(msg, duration, withStickyActionBar, 'pending'),
      information: (msg, duration, withStickyActionBar) =>
        dispatchNotification(msg, duration, withStickyActionBar, 'information'),
      close: () => dispatchCloseNotification(),
    }),
    [dispatchCloseNotification, dispatchNotification]
  )
}

export default useNotification
