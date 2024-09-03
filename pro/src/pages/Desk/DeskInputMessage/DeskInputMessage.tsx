import classNames from 'classnames'

import styles from './DeskInputMessage.module.scss'

export function DeskInputMessage({
  message,
  isError = false,
}: {
  message: string
  isError?: boolean
}) {
  return (
    <div
      className={classNames(styles['desk-message'], {
        [styles['error']]: isError,
      })}
      data-testid="desk-message"
    >
      {message}
    </div>
  )
}
