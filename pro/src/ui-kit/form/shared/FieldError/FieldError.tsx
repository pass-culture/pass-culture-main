import cn from 'classnames'

import strokeErrorIcon from '@/icons/stroke-error.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './FieldError.module.scss'

interface FieldErrorProps {
  children: React.ReactNode | React.ReactNode[]
  className?: string
  name?: string
  iconAlt?: string
}

export const FieldError = ({
  children,
  className,
  name,
  iconAlt = '',
}: FieldErrorProps): JSX.Element => (
  <div className={cn(styles['field-error'], className)}>
    <SvgIcon src={strokeErrorIcon} alt={iconAlt} width="16" />
    <span className={styles['field-error-text']} data-testid={`error-${name}`}>
      {children}
    </span>
  </div>
)
