import cn from 'classnames'
import React from 'react'

import { NotificationTypeEnum } from 'hooks/useNotification'
import fullErrorIcon from 'icons/full-error.svg'
import fullInfoIcon from 'icons/full-info.svg'
import fullValidateIcon from 'icons/full-validate.svg'
import strokeClockIcon from 'icons/stroke-clock.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './Notification.module.scss'

interface Notification {
  text: string | null
  type: NotificationTypeEnum
  duration?: number
}

interface NotificationToasterProps {
  notification: Notification | null
  isVisible: boolean
  isStickyBarOpen: boolean
}

export const notificationAdditionalAttributes: {
  [key in NotificationTypeEnum]: Partial<React.HTMLAttributes<HTMLDivElement>>
} = {
  [NotificationTypeEnum.ERROR]: { role: 'alert' },
  [NotificationTypeEnum.SUCCESS]: { role: 'status' },
  [NotificationTypeEnum.PENDING]: { ['aria-live']: 'polite' },
  [NotificationTypeEnum.INFORMATION]: { role: 'status' },
}

function getNotificationContent(notification: Notification) {
  const type = notification.type

  let icon = fullValidateIcon
  /* istanbul ignore next: DEBT, TO FIX */
  if (type === 'error') {
    icon = fullErrorIcon
  } else if (type === 'pending') {
    icon = strokeClockIcon
  } else if (type === 'information') {
    icon = fullInfoIcon
  }

  return (
    <>
      <SvgIcon className={styles['icon']} src={icon} alt="" />
      {notification.text}
    </>
  )
}

export const NotificationToaster = ({
  notification,
  isVisible,
  isStickyBarOpen,
}: NotificationToasterProps): JSX.Element => {
  const notificationTypes = Object.values(NotificationTypeEnum)

  const notifContent = notification
    ? getNotificationContent(notification)
    : null

  return (
    <>
      {notificationTypes.map((type) => {
        const isCurrentNotifType = type === notification?.type
        return (
          <div
            key={type}
            data-testid={`global-notification-${type}`}
            {...notificationAdditionalAttributes[type]}
          >
            <div
              className={cn(
                styles['notification'],
                styles[`is-${type}`],
                isVisible && isCurrentNotifType
                  ? styles['show']
                  : styles['hide'],
                isStickyBarOpen && styles['with-sticky-action-bar']
              )}
            >
              {isCurrentNotifType ? notifContent : null}
            </div>
          </div>
        )
      })}
    </>
  )
}
