import classNames from 'classnames'
import { ForwardedRef, forwardRef, useId } from 'react'

import { SelectOption } from '@/commons/custom_types/form'
import { SelectInput } from '@/ui-kit/form/shared/BaseSelectInput/SelectInput'
import { FieldError } from '@/ui-kit/form/shared/FieldError/FieldError'

import styles from './Select.module.scss'

type SelectProps<T extends number | string = string> = {
  /** Name of the input. Used for identifying it in an uncontrolled form, and for referencing the error */
  name: string
  className?: string
  required?: boolean
  disabled?: boolean
  label: string | React.ReactNode
  onChange?: React.InputHTMLAttributes<HTMLSelectElement>['onChange']
  onBlur?: React.FocusEventHandler<HTMLSelectElement>
  /** Option displayed if no option of the option list is selected */
  defaultOption?: SelectOption<T> | null
  options: SelectOption<T>[]
  /** Whether or not to display the asterisk in the label when the field is required */
  asterisk?: boolean
  error?: string
  value?: string
  ariaLabel?: string
}

export const Select = forwardRef(
  (
    {
      name,
      defaultOption = null,
      options,
      className,
      required,
      disabled,
      label,
      onChange,
      onBlur,
      error,
      asterisk = true,
      value,
      ariaLabel,
    }: SelectProps<string | number>,
    ref: ForwardedRef<HTMLSelectElement>
  ): JSX.Element => {
    const labelId = useId()
    const errorId = useId()

    return (
      <div className={classNames(styles['select'], className)}>
        <div className={styles['select-field']}>
          <label htmlFor={labelId} className={styles['label']}>
            {label}
            {required && asterisk ? ' *' : ''}
          </label>
          <SelectInput
            disabled={disabled}
            hasError={Boolean(error)}
            options={options}
            defaultOption={defaultOption}
            aria-required={required}
            onBlur={onBlur}
            onChange={onChange}
            name={name}
            value={value}
            aria-describedby={errorId}
            ref={ref}
            id={labelId}
            aria-label={ariaLabel}
          />
        </div>
        <div role="alert" id={errorId}>
          {error && (
            <FieldError name={name} className={styles['error']}>
              {error}
            </FieldError>
          )}
        </div>
      </div>
    )
  }
)

Select.displayName = 'Select'
