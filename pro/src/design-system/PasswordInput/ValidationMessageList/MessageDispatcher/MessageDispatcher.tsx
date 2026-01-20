import cn from 'classnames'

import fullErrorIcon from '@/icons/full-clear.svg'
import fullValidIcon from '@/icons/full-validate.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './MessageDispatcher.module.scss'

type MessageDispatcherProps = {
  isPristine: boolean
  isOnError: boolean
  message: string
}

export const MessageDispatcher = ({
  isPristine,
  isOnError,
  message,
}: MessageDispatcherProps): JSX.Element => {
  if (isPristine) {
    return <MessagePristine message={message} />
  }

  return isOnError ? (
    <MessageError message={message} />
  ) : (
    <MessageSuccess message={message} />
  )
}

type MessageProps = {
  message: string
}

const MessageSuccess = ({ message }: MessageProps): JSX.Element => (
  <div
    className={cn(styles['message'], styles['message-success'])}
    data-testid={`success-${message}`}
  >
    <SvgIcon src={fullValidIcon} alt={''} width="16" />
    <span className={styles['message-success-text']}>{message}</span>
  </div>
)

const MessageError = ({ message }: MessageProps): JSX.Element => (
  <div
    className={cn(styles['message'], styles['message-error'])}
    data-testid={`error-${message}`}
  >
    <SvgIcon src={fullErrorIcon} alt={''} width="16" />
    <span className={styles['message-error-text']}>{message}</span>
  </div>
)

const MessagePristine = ({ message }: MessageProps): JSX.Element => (
  <div className={cn(styles['message'], styles['message-pristine'])}>
    <span className={styles['message-error-text']}>{message}</span>
  </div>
)
