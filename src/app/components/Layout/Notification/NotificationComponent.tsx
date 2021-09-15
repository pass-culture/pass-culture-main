import React, { useEffect, useState } from "react"

import {
  NOTIFICATION_SHOW_DURATION,
  NOTIFICATION_TRANSITION_DURATION,
} from "./_constants.js"
import { ReactComponent as ErrorIcon } from "./assets/notification-error-white.svg"
import { ReactComponent as SuccessIcon } from "./assets/notification-success-white.svg"
import { Notification, NotificationType } from "./Notification"

export const NotificationComponent = ({
  notification,
  setNotification,
}: {
  notification: Notification | null;
  setNotification: (notification: Notification | null) => void;
}): JSX.Element | null => {
  const [isVisible, setIsVisible] = useState(false)
  const [isInDom, setIsInDom] = useState(false)

  useEffect(() => {
    let timer
    if (notification) {
      setIsVisible(true)
      setIsInDom(true)
      timer = setTimeout(() => setIsVisible(false), NOTIFICATION_SHOW_DURATION)
    }
    return () => clearTimeout(timer)
  }, [notification])

  useEffect(() => {
    let timer
    if (!isVisible && notification) {
      timer = setTimeout(() => {
        setIsInDom(false)
        setNotification(null)
      }, NOTIFICATION_TRANSITION_DURATION)
    }
    return () => clearTimeout(timer)
  }, [isVisible, notification, setNotification])

  let iconComponent = <SuccessIcon />
  if (notification?.type === NotificationType.error) {
    iconComponent = <ErrorIcon />
  }

  if (notification && isInDom) {
    return (
      <div
        className={`notification is-${notification.type || "info"} ${
          isVisible ? "show" : "hide"
        }`}
      >
        {iconComponent}
        {notification.text}
      </div>
    )
  } else {
    return null
  }
}
