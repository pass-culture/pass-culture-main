import PropTypes from 'prop-types'
import React, { useEffect, useState } from 'react'

import Icon from 'components/layout/Icon'

import { NOTIFICATION_SHOW_DURATION, NOTIFICATION_TRANSITION_DURATION } from './_constants'

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
  let svg
  if (type === 'success') {
    svg = 'ico-notification-success-white'
  } else if (type === 'error') {
    svg = 'ico-notification-error-white'
  }

  if (isInDom) {
    return (
      <div className={`notification is-${type || 'info'} ${isVisible ? 'show' : 'hide'}`}>
        <Icon svg={svg} />
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
    text: PropTypes.string,
    type: PropTypes.string,
  }).isRequired,
}

export default Notification
