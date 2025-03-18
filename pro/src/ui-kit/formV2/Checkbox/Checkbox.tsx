import cn from 'classnames'
import { ForwardedRef, forwardRef, useId } from 'react'

import {
  BaseCheckbox,
  CheckboxVariant,
} from 'ui-kit/form/shared/BaseCheckbox/BaseCheckbox'
import { FieldError } from 'ui-kit/form/shared/FieldError/FieldError'

import styles from './Checkbox.module.scss'

export interface CheckboxProps {
  /** Name of the input. Used for identifying it in an uncontrolled form, and for referencing the error */
  name: string
  className?: string
  /** Error text for the checkbox */
  error?: string
  /** Whether or not to display the error message. If false, the field has the error styles but no message */
  displayErrorMessage?: boolean
  onChange?: React.InputHTMLAttributes<HTMLInputElement>['onChange']
  onBlur?: React.InputHTMLAttributes<HTMLInputElement>['onBlur']
  label: string | React.ReactNode
  checked?: boolean
  partialCheck?: boolean
  icon?: string
  disabled?: boolean
  variant?: CheckboxVariant
  childrenOnChecked?: JSX.Element
}

export const Checkbox = forwardRef(
  (
    {
      name,
      className,
      error,
      displayErrorMessage = true,
      ...props
    }: CheckboxProps,
    ref: ForwardedRef<HTMLInputElement>
  ): JSX.Element => {
    const errorId = useId()

    return (
      <div className={cn(styles['checkbox'], className)}>
        <BaseCheckbox
          hasError={Boolean(error)}
          {...props}
          name={name}
          ref={ref}
          aria-describedby={errorId}
        />
        <div role="alert" id={errorId}>
          {error && displayErrorMessage && (
            <FieldError name={name} className={styles['error']}>
              {error}
            </FieldError>
          )}
        </div>
      </div>
    )
  }
)

Checkbox.displayName = 'Checkbox'
