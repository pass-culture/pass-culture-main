import cn from 'classnames'
import { useField } from 'formik'
import React from 'react'

import { BaseCheckbox, FieldError } from '../shared'

import styles from './Checkbox.module.scss'

interface ICheckboxProps {
  name: string
  value: string
  label: string
  className?: string
  hideFooter?: boolean
  Icon?: React.FunctionComponent<
    React.SVGProps<SVGSVGElement> & {
      title?: string | undefined
    }
  >
  disabled?: boolean
}

const Checkbox = ({
  name,
  value,
  label,
  className,
  Icon,
  hideFooter,
  disabled,
}: ICheckboxProps): JSX.Element => {
  const [field, meta] = useField({ name, type: 'checkbox' })
  return (
    <div className={cn(styles['checkbox'], className)}>
      <BaseCheckbox
        {...field}
        Icon={Icon}
        hasError={meta.touched && !!meta.error}
        label={label}
        value={value}
        disabled={disabled}
      />
      {!hideFooter && (
        <div className={styles['checkbox-error']}>
          {meta.touched && !!meta.error && (
            <FieldError name={name}>{meta.error}</FieldError>
          )}
        </div>
      )}
    </div>
  )
}

export default Checkbox
