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

export interface NotificationToasterProps {
  notification: Notification
  isVisible: boolean
  isStickyBarOpen: boolean
}

const NotificationToaster = ({
  notification,
  isVisible,
  isStickyBarOpen,
}: NotificationToasterProps): JSX.Element => {
  const { text, type } = notification

  const notificationAttribute = {
    [NotificationTypeEnum.ERROR]: 'alert',
    [NotificationTypeEnum.SUCCESS]: 'status',
    [NotificationTypeEnum.PENDING]: 'progressbar',
    [NotificationTypeEnum.INFORMATION]: 'status',
  }[type]

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
      <SvgIcon className={styles['icon']} src={icon} alt="" />
      {text}
    </div>
  )
}
export default NotificationToaster
