import cn from 'classnames'
import { useField } from 'formik'
import { ForwardedRef } from 'react'

import {
  BaseCheckbox,
  BaseCheckboxProps,
} from 'ui-kit/form/shared/BaseCheckbox/BaseCheckbox'

import { FieldError } from '../shared/FieldError/FieldError'

import styles from './Checkbox.module.scss'

interface CheckboxProps extends BaseCheckboxProps {
  name: string
  className?: string
  hideFooter?: boolean
  /**
   * A forward ref to the input element.
   */
  refForInput?: ForwardedRef<HTMLInputElement>
}

export const Checkbox = ({
  name,
  className,
  hideFooter,
  refForInput,
  ...props
}: CheckboxProps): JSX.Element => {
  const [field, meta] = useField({ name, type: 'checkbox' })
  const hasError = meta.touched && !!meta.error
  return (
    <div className={cn(styles['checkbox'], className)}>
      <BaseCheckbox
        ref={refForInput}
        hasError={hasError}
        {...field}
        {...props}
      />
      {!hideFooter && (
        <div className={styles['checkbox-error']}>
          {hasError && <FieldError name={name}>{meta.error}</FieldError>}
        </div>
      )}
    </div>
  )
}
