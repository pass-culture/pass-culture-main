import React, { useEffect, useState } from 'react'
import { useSelector } from 'react-redux'

import useNotification from 'components/hooks/useNotification'
import { notificationSelector } from 'store/selectors/notificationSelector'

import {
  NOTIFICATION_SHOW_DURATION,
  NOTIFICATION_TRANSITION_DURATION,
} from './_constants'
import { ReactComponent as ErrorIcon } from './assets/notification-error-white.svg'
import { ReactComponent as InfoIcon } from './assets/notification-information.svg'
import { ReactComponent as SuccessIcon } from './assets/notification-success-white.svg'
import { ReactComponent as PendingIcon } from './assets/status-pending.svg'

const Notification = (): JSX.Element | null => {
  const [isVisible, setIsVisible] = useState(false)
  const [isInDom, setIsInDom] = useState(false)
  const notification = useSelector(notificationSelector)
  const notificationHook = useNotification()

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
        notificationHook.close()
      }, NOTIFICATION_TRANSITION_DURATION)
      return () => clearTimeout(timer)
    }
    return () => undefined
  }, [isVisible, notification])

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
