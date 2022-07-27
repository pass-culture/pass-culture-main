import React, { useEffect, useState } from 'react'

import {
  NOTIFICATION_SHOW_DURATION,
  NOTIFICATION_TRANSITION_DURATION,
} from './_constants'
import { ReactComponent as ErrorIcon } from './assets/notification-error-white.svg'
import { ReactComponent as InfoIcon } from './assets/notification-information.svg'
import { ReactComponent as SuccessIcon } from './assets/notification-success-white.svg'
import { ReactComponent as PendingIcon } from './assets/status-pending.svg'

interface INotification {
  text: React.ReactNode
  type: 'error' | 'success' | 'pending' | 'information'
}

type INotificationProps = {
  hideNotification: () => void
  notification?: INotification | null
  children?: never
}

const Notification = ({
  hideNotification,
  notification,
}: INotificationProps): JSX.Element | null => {
  const [isVisible, setIsVisible] = useState(false)
  const [isInDom, setIsInDom] = useState(false)

  useEffect(() => {
    if (notification && notification.text) {
      setIsVisible(true)
      setIsInDom(true)
      const timer = setTimeout(
        () => setIsVisible(false),
        NOTIFICATION_SHOW_DURATION
      )
      return () => clearTimeout(timer)
    }
    return () => undefined
  }, [notification])

  useEffect(() => {
    if (!isVisible && notification && notification.text) {
      const timer = setTimeout(() => {
        setIsInDom(false)
        hideNotification()
      }, NOTIFICATION_TRANSITION_DURATION)
      return () => clearTimeout(timer)
    }
    return () => undefined
  }, [hideNotification, isVisible, notification])

  if (!notification) {
    return null
  }

  const { text, type } = notification
  let iconComponent = <SuccessIcon />
  if (type === 'error') {
    iconComponent = <ErrorIcon />
  } else if (type === 'pending') {
    iconComponent = <PendingIcon />
  } else if (type === 'information') {
    iconComponent = <InfoIcon />
  }

  if (isInDom) {
    return (
      <div
        className={`notification is-${type || 'info'} ${
          isVisible ? 'show' : 'hide'
        }`}
      >
        {iconComponent}
        {text}
      </div>
    )
  } else {
    return null
  }
}

export default Notification
