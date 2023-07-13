import './Notification.scss'

import React, { useEffect, useState } from 'react'

import fullErrorIcon from 'icons/full-error.svg'
import fullValidateIcon from 'icons/full-validate.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import {
  NOTIFICATION_SHOW_DURATION,
  NOTIFICATION_TRANSITION_DURATION,
} from './_constants'

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
    let timer: string | number | NodeJS.Timeout | undefined
    if (notification) {
      setIsVisible(true)
      setIsInDom(true)
      timer = setTimeout(() => setIsVisible(false), NOTIFICATION_SHOW_DURATION)
    }
    return () => clearTimeout(timer)
  }, [notification])

  useEffect(() => {
    let timer: string | number | NodeJS.Timeout | undefined
    if (!isVisible && notification) {
      timer = setTimeout(() => {
        setIsInDom(false)
      }, NOTIFICATION_TRANSITION_DURATION)
    }
    return () => clearTimeout(timer)
  }, [isVisible, notification])

  let icon = fullValidateIcon
  if (notification?.type === NotificationType.error) {
    icon = fullErrorIcon
  }

  if (notification && isInDom) {
    return (
      <div
        className={`notification is-${notification.type || 'info'} ${
          isVisible ? 'show' : 'hide'
        }`}
      >
        <SvgIcon src={icon} alt="" />
        {notification.text}
      </div>
    )
  } else {
    return null
  }
}
