import cn from 'classnames'

import strokeValidIcon from '@/icons/stroke-valid.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './FieldSuccess.module.scss'

interface FieldSuccessProps {
  children: React.ReactNode | React.ReactNode[]
  className?: string
  name: string
  iconAlt?: string
}

export const FieldSuccess = ({
  children,
  className,
  name,
  iconAlt = '',
}: FieldSuccessProps): JSX.Element => (
  <div className={cn(styles['field-success'], className)} id={name}>
    <SvgIcon src={strokeValidIcon} alt={iconAlt} width="16" />
    <span
      className={styles['field-success-text']}
      data-testid={`success-${name}`}
      role="alert"
    >
      {children}
    </span>
  </div>
)
