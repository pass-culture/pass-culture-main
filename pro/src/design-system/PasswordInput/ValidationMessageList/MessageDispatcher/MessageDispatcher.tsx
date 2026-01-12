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
  return isPristine ? (
    <MessagePristine message={message} />
  ) : isOnError ? (
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
    className={cn(styles['field'], styles['field-success'])}
    data-testid={`success-${message}`}
  >
    <SvgIcon src={fullValidIcon} alt={''} width="16" />
    <span className={styles['sr-only']}>Il y a bien</span>
    <span className={styles['field-success-text']}>{message}</span>
  </div>
)

const MessageError = ({ message }: MessageProps): JSX.Element => (
  <div
    className={cn(styles['field'], styles['field-error'])}
    data-testid={`error-${message}`}
  >
    <SvgIcon src={fullErrorIcon} alt={''} width="16" />
    <span className={styles['sr-only']}>Il manque</span>
    <span className={styles['field-error-text']}>{message}</span>
  </div>
)

const MessagePristine = ({ message }: MessageProps): JSX.Element => (
  <div className={cn(styles['field'], styles['field-pristine'])}>
    <span className={styles['field-error-text']}>{message}</span>
  </div>
)
