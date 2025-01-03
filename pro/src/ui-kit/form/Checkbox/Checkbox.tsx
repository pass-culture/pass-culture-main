import cn from 'classnames'
import { useField } from 'formik'

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
}

export const Checkbox = ({
  name,
  className,
  hideFooter,
  ...props
}: CheckboxProps): JSX.Element => {
  const [field, meta] = useField({ name, type: 'checkbox' })
  const hasError = meta.touched && !!meta.error
  return (
    <div className={cn(styles['checkbox'], className)}>
      <BaseCheckbox hasError={hasError} {...field} {...props} />
      {!hideFooter && (
        <div className={styles['checkbox-error']}>
          {hasError && <FieldError name={name}>{meta.error}</FieldError>}
        </div>
      )}
    </div>
  )
}
