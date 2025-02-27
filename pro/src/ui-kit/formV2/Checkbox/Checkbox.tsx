import cn from 'classnames'

import {
  BaseCheckbox,
  BaseCheckboxProps,
} from 'ui-kit/form/shared/BaseCheckbox/BaseCheckbox'
import { FieldError } from 'ui-kit/form/shared/FieldError/FieldError'

import styles from './Checkbox.module.scss'

export interface CheckboxProps extends BaseCheckboxProps {
  name: string
  className?: string
  hideFooter?: boolean
  error?: string
}

export const Checkbox = ({
  name,
  className,
  hideFooter,
  error,
  ...props
}: CheckboxProps): JSX.Element => {
  return (
    <div className={cn(styles['checkbox'], className)}>
      <BaseCheckbox hasError={!!error} {...props} />
      {!hideFooter && (
        <div className={styles['checkbox-error']}>
          {error && <FieldError name={name}>{error}</FieldError>}
        </div>
      )}
    </div>
  )
}
