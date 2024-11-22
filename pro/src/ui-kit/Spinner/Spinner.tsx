import cn from 'classnames'

import strokePass from 'icons/stroke-pass.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './Spinner.module.scss'

interface SpinnerProps {
  message?: string
  className?: string
  /**
   * A custom test id to target the component
   * when running tests.
   */
  testId?: string
}

export const Spinner = ({
  message = 'Chargement en cours',
  className,
  testId = 'spinner'
}: SpinnerProps): JSX.Element => {
  return (
    <div
      className={cn(styles['loading-spinner'], className)}
      data-testid={testId}
    >
      <SvgIcon
        src={strokePass}
        alt=""
        className={styles['loading-spinner-icon']}
      />

      <div className={styles['content']}>{message}</div>
    </div>
  )
}
