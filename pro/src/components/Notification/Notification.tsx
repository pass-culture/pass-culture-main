import cn from 'classnames'
import React, { useEffect, useState } from 'react'
import { useSelector } from 'react-redux'

import { NOTIFICATION_TRANSITION_DURATION } from 'core/Notification/constants'
import useNotification, { NotificationTypeEnum } from 'hooks/useNotification'
import {
  isStickyBarOpenSelector,
  notificationSelector,
} from 'store/selectors/notificationSelector'

import { ReactComponent as ErrorIcon } from './assets/notification-error-white.svg'
import { ReactComponent as InfoIcon } from './assets/notification-information.svg'
import { ReactComponent as SuccessIcon } from './assets/notification-success-white.svg'
import { ReactComponent as PendingIcon } from './assets/status-pending.svg'
import styles from './Notification.module.scss'

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

  if (!notification) {
    return null
  }

  const { text, type } = notification
  let iconComponent = <SuccessIcon />
  /* istanbul ignore next: DEBT, TO FIX */
  if (type === 'error') {
    iconComponent = <ErrorIcon />
  } else if (type === 'pending') {
    iconComponent = <PendingIcon />
  } else if (type === 'information') {
    iconComponent = <InfoIcon />
  }

  const notificationAttribute = {
    [NotificationTypeEnum.ERROR]: 'alert',
    [NotificationTypeEnum.SUCCESS]: 'status',
    [NotificationTypeEnum.PENDING]: 'progressbar',
    [NotificationTypeEnum.INFORMATION]: 'status',
  }[type]

  if (isInDom) {
    return (
      <div
        data-testid={`global-notification-${type}`}
        className={
          /* istanbul ignore next */
          cn(
            styles['notification'],
            styles[
              //graphic variation
              /* istanbul ignore next */ `is-${type || 'success'}`
            ],
            /* istanbul ignore next: DEBT, TO FIX */ isVisible
              ? styles['show']
              : styles['hide'],
            /* istanbul ignore next: DEBT, TO FIX */ isStickyBarOpen &&
              styles['with-sticky-action-bar']
          )
        }
        role={notificationAttribute ?? 'status'}
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
