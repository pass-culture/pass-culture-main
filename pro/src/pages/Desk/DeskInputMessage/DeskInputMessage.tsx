import classNames from 'classnames'

import { MESSAGE_VARIANT } from '../types'
import styles from './DeskInputMessage.module.scss'

export function DeskInputMessage({
  message,
  variant = MESSAGE_VARIANT.DEFAULT,
}: {
  message: string
  variant?: MESSAGE_VARIANT
}) {
  return (
    <div
      className={classNames(
        styles['desk-message'],
        styles[`desk-message-${variant}`]
      )}
      data-testid="desk-message"
    >
      {message}
    </div>
  )
}
