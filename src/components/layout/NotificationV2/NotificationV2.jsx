import PropTypes from 'prop-types'
import React, { useEffect, useState } from 'react'

import Icon from 'components/layout/Icon'

import { NOTIFICATION_SHOW_DURATION, NOTIFICATION_TRANSITION_DURATION } from './_constants'

const NotificationV2 = ({ hideNotification, notification }) => {
  const [isVisible, setIsVisible] = useState(false)
  useEffect(() => {
    let timer
    if (notification.text) {
      setIsVisible(true)
      timer = setTimeout(() => setIsVisible(false), NOTIFICATION_SHOW_DURATION)
    }
    return () => clearTimeout(timer)
  }, [notification.text])

  useEffect(() => {
    let timer
    if (!isVisible && notification.text) {
      timer = setTimeout(() => hideNotification(), NOTIFICATION_TRANSITION_DURATION)
    }
    return () => clearTimeout(timer)
  }, [hideNotification, isVisible, notification.text])

  const { text, type } = notification
  let svg
  if (type === 'success') {
    svg = 'ico-notification-success-white'
  }

  return (
    <div className={`notification-v2 is-${type || 'info'} ${isVisible ? 'show' : 'hide'}`}>
      <Icon svg={svg} />
      {text}
    </div>
  )
}

NotificationV2.propTypes = {
  hideNotification: PropTypes.func.isRequired,
  notification: PropTypes.shape({
    text: PropTypes.string,
    type: PropTypes.string,
  }).isRequired,
}

export default NotificationV2
