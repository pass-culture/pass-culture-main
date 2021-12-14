import { useCallback, useMemo } from 'react'
import { useDispatch } from 'react-redux'

import { showNotification } from 'store/reducers/notificationReducer'

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

  return useMemo(
    () => ({
      success: msg => dispatchNotification(msg, 'success'),
      error: msg => dispatchNotification(msg, 'error'),
      pending: msg => dispatchNotification(msg, 'pending'),
      information: msg => dispatchNotification(msg, 'information'),
    }),
    [dispatchNotification]
  )
}

export default useNotification
