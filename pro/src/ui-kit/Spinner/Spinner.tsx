import cn from 'classnames'

import strokePass from 'icons/stroke-pass.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './Spinner.module.scss'

interface SpinnerProps {
  message?: string
  className?: string
}

export const Spinner = ({
  message = 'Chargement en cours',
  className,
}: SpinnerProps): JSX.Element => {
  return (
    <div
      className={cn(styles['loading-spinner'], className)}
      data-testid="spinner"
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
