/*
 * @debt directory "Gaël: this file should be migrated within the new directory structure"
 */

import PropTypes from 'prop-types'
import React, { useEffect, useState } from 'react'

import { NOTIFICATION_SHOW_DURATION, NOTIFICATION_TRANSITION_DURATION } from './_constants'
import { ReactComponent as ErrorIcon } from './assets/notification-error-white.svg'
import { ReactComponent as InfoIcon } from './assets/notification-information.svg'
import { ReactComponent as SuccessIcon } from './assets/notification-success-white.svg'
import { ReactComponent as PendingIcon } from './assets/status-pending.svg'

const Notification = ({ hideNotification, notification }) => {
  const [isVisible, setIsVisible] = useState(false)
  const [isInDom, setIsInDom] = useState(false)

  useEffect(() => {
    let timer
    if (notification.text) {
      setIsVisible(true)
      setIsInDom(true)
      timer = setTimeout(() => setIsVisible(false), NOTIFICATION_SHOW_DURATION)
    }
    return () => clearTimeout(timer)
  }, [notification.text])

  useEffect(() => {
    let timer
    if (!isVisible && notification.text) {
      timer = setTimeout(() => {
        setIsInDom(false)
        hideNotification()
      }, NOTIFICATION_TRANSITION_DURATION)
    }
    return () => clearTimeout(timer)
  }, [hideNotification, isVisible, notification.text])

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
      <div className={`notification is-${type || 'info'} ${isVisible ? 'show' : 'hide'}`}>
        {iconComponent}
        {text}
      </div>
    )
  } else {
    return null
  }
}

Notification.propTypes = {
  hideNotification: PropTypes.func.isRequired,
  notification: PropTypes.shape({
    text: PropTypes.oneOfType([PropTypes.string, PropTypes.shape()]),
    type: PropTypes.oneOf(['error', 'success', 'pending', 'information']),
  }).isRequired,
}

export default Notification
