import { useDispatch } from 'react-redux'

import { showNotification } from 'store/reducers/notificationReducer'

const useNotification = () => {
  const dispatch = useDispatch()
  const dispatchNotification = (textMessage, type) => {
    dispatch(
      showNotification({
        text: textMessage,
        type: type,
      })
    )
  }

  return {
    success: (msg) => dispatchNotification(msg, 'success'),
    error: (msg) => dispatchNotification(msg, 'error'),
    pending: (msg) => dispatchNotification(msg, 'pending'),
    information: (msg) => dispatchNotification(msg, 'information'),
  }
}

export default useNotification
