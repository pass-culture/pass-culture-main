import cn from 'classnames'

import { NotificationTypeEnum } from 'commons/hooks/useNotification'
import fullErrorIcon from 'icons/full-error.svg'
import fullInfoIcon from 'icons/full-info.svg'
import fullValidateIcon from 'icons/full-validate.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './Notification.module.scss'

/**
 * Represents a notification with text, type, and optional duration.
 */
interface Notification {
  /**
   * The text content of the notification.
   */
  text: string | null
  /**
   * The type of the notification, indicating its purpose.
   */
  type: NotificationTypeEnum
  /**
   * The duration for which the notification is displayed.
   */
  duration?: number
}

/**
 * Props for the NotificationToaster component.
 */
interface NotificationToasterProps {
  /**
   * The notification to display.
   */
  notification: Notification | null
  /**
   * Indicates if the notification toaster is visible.
   */
  isVisible: boolean
  /**
   * Indicates if the sticky action bar is open.
   */
  isStickyBarOpen: boolean
}

/**
 * Additional attributes for notifications based on their type.
 */
export const notificationAdditionalAttributes: {
  [key in NotificationTypeEnum]: Partial<React.HTMLAttributes<HTMLDivElement>>
} = {
  [NotificationTypeEnum.ERROR]: { role: 'alert' },
  [NotificationTypeEnum.SUCCESS]: { role: 'status' },
  [NotificationTypeEnum.INFORMATION]: { role: 'status' },
}

/**
 * Gets the content for a notification based on its type.
 *
 * @param {Notification} notification - The notification to get content for.
 * @returns {JSX.Element} The notification content.
 */
function getNotificationContent(notification: Notification): JSX.Element {
  const type = notification.type

  let icon = fullValidateIcon
  /* istanbul ignore next: DEBT, TO FIX */
  if (type === 'error') {
    icon = fullErrorIcon
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

/**
 * The NotificationToaster component is used to display notifications of different types.
 * It supports displaying notifications such as errors, information, success, or pending messages.
 *
 * ---
 * **Important: Use `notification` prop to provide the information to be displayed.**
 * ---
 *
 * @param {NotificationToasterProps} props - The props for the NotificationToaster component.
 * @returns {JSX.Element} The rendered NotificationToaster component.
 *
 * @example
 * <NotificationToaster
 *   notification={{ text: 'Operation successful', type: NotificationTypeEnum.SUCCESS }}
 *   isVisible={true}
 *   isStickyBarOpen={false}
 * />
 *
 * @accessibility
 * - **Role and Aria Attributes**: The component uses roles such as `alert` or `status` to convey the nature of the notification to screen readers.
 * - **Icons**: Icons are included to provide visual representation of the notification type, making it easier for users to understand.
 */
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
