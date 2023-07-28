import React, { useEffect, useState } from 'react'
import { useSelector } from 'react-redux'

import { NOTIFICATION_TRANSITION_DURATION } from 'core/Notification/constants'
import useNotification from 'hooks/useNotification'
import {
  isStickyBarOpenSelector,
  notificationSelector,
} from 'store/selectors/notificationSelector'
import NotificationToaster from 'ui-kit/NotificationToaster/NotificationToaster'

const Notification = (): JSX.Element | null => {
  const [isVisible, setIsVisible] = useState(false)
  const [isInDom, setIsInDom] = useState(false)
  const notification = useSelector(notificationSelector)
  const isStickyBarOpen = useSelector(isStickyBarOpenSelector)
  const notificationHook = useNotification()

  useEffect(() => {
    if (notification && notification.text) {
      setIsVisible(true)
      setIsInDom(true)
      const timer = setTimeout(() => setIsVisible(false), notification.duration)
      return () => clearTimeout(timer)
    }
    return () => undefined
  }, [notification])

  useEffect(() => {
    if (!isVisible && notification && notification.text) {
      const timer = setTimeout(() => {
        /* istanbul ignore next: DEBT, TO FIX */
        setIsInDom(false)
        /* istanbul ignore next: DEBT, TO FIX */
        notificationHook.close()
      }, NOTIFICATION_TRANSITION_DURATION)
      return () => clearTimeout(timer)
    }
    return () => undefined
  }, [isVisible, notification])

  if (!notification || !isInDom) {
    return null
  }

  return (
    <NotificationToaster
      notification={notification}
      isVisible={isVisible}
      isStickyBarOpen={isStickyBarOpen}
    />
  )
}

export default Notification
