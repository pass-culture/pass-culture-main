import { BaseCheckbox, FieldError } from '../shared'

import React from 'react'
import cn from 'classnames'
import styles from './Checkbox.module.scss'
import { useField } from 'formik'

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
}

const Checkbox = ({
  name,
  value,
  label,
  className,
  Icon,
  hideFooter,
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
