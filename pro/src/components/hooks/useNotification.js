import { useCallback, useMemo } from 'react'
import { useDispatch } from 'react-redux'

import {
  closeNotification,
  showNotification,
} from 'store/reducers/notificationReducer'

const useNotification = () => {
  const dispatch = useDispatch()
  const dispatchNotification = useCallback(
    (textMessage, type) => {
      dispatch(
        showNotification({
          text: textMessage,
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
      success: msg => dispatchNotification(msg, 'success'),
      error: msg => dispatchNotification(msg, 'error'),
      pending: msg => dispatchNotification(msg, 'pending'),
      information: msg => dispatchNotification(msg, 'information'),
      close: () => dispatchCloseNotification(),
    }),
    [dispatchCloseNotification, dispatchNotification]
  )
}

export default useNotification
