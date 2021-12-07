import './Notification.scss'

import React, { useEffect, useState } from 'react'

import {
  NOTIFICATION_SHOW_DURATION,
  NOTIFICATION_TRANSITION_DURATION,
} from './_constants'
import { ReactComponent as ErrorIcon } from './assets/notification-error-white.svg'
import { ReactComponent as SuccessIcon } from './assets/notification-success-white.svg'

export enum NotificationType {
  success = 'success',
  error = 'error',
}

export class Notification {
  text: string
  type: NotificationType

  constructor(type: NotificationType, text: string) {
    this.text = text
    this.type = type
  }
}

export const NotificationComponent = ({
  notification,
}: {
  notification: Notification | null
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
      }, NOTIFICATION_TRANSITION_DURATION)
    }
    return () => clearTimeout(timer)
  }, [isVisible, notification])

  let iconComponent = <SuccessIcon />
  if (notification?.type === NotificationType.error) {
    iconComponent = <ErrorIcon />
  }

  if (notification && isInDom) {
    return (
      <div
        className={`notification is-${notification.type || 'info'} ${
          isVisible ? 'show' : 'hide'
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
