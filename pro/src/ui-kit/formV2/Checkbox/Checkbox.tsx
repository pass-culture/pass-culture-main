import cn from 'classnames'
import { ForwardedRef, forwardRef } from 'react'

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

export const Checkbox = forwardRef(
  (
    { name, className, hideFooter, error, ...props }: CheckboxProps,
    ref: ForwardedRef<HTMLInputElement>
  ): JSX.Element => {
    return (
      <div className={cn(styles['checkbox'], className)}>
        <BaseCheckbox hasError={!!error} {...props} name={name} ref={ref} />
        {!hideFooter && (
          <div className={styles['checkbox-error']}>
            {error && <FieldError name={name}>{error}</FieldError>}
          </div>
        )}
      </div>
    )
  }
)

Checkbox.displayName = 'Checkbox'
