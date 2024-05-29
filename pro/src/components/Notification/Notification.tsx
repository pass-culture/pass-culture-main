import React, { useEffect, useState } from 'react'
import { useSelector } from 'react-redux'

import { NOTIFICATION_TRANSITION_DURATION } from 'core/Notification/constants'
import { useNotification } from 'hooks/useNotification'
import {
  isStickyBarOpenSelector,
  notificationSelector,
} from 'store/notifications/selectors'
import { NotificationToaster } from 'ui-kit/NotificationToaster/NotificationToaster'

export const Notification = (): JSX.Element | null => {
  const [isVisible, setIsVisible] = useState(false)
  const [isInDom, setIsInDom] = useState(false)
  const notification = useSelector(notificationSelector)
  const isStickyBarOpen = useSelector(isStickyBarOpenSelector)
  const notificationHook = useNotification()

  useEffect(() => {
    if (!notification?.text || notification.duration === undefined) {
      return () => undefined
    }

    setIsVisible(true)
    setIsInDom(true)

    const hideNotificationTimer = setTimeout(() => {
      setIsVisible(false)
    }, notification.duration)

    const removeNotificationFromDOMTimer = setTimeout(() => {
      setIsInDom(false)
      notificationHook.close()
    }, notification.duration + NOTIFICATION_TRANSITION_DURATION)

    return () => {
      clearTimeout(hideNotificationTimer)
      clearTimeout(removeNotificationFromDOMTimer)
    }
  }, [notification])

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
