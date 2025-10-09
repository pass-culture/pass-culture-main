import classNames from 'classnames'
import { type ForwardedRef, forwardRef, useId } from 'react'

import type { SelectOption } from '@/commons/custom_types/form'
import { FieldFooter } from '@/design-system/common/FieldFooter/FieldFooter'
import { FieldHeader } from '@/design-system/common/FieldHeader/FieldHeader'
import { SelectInput } from '@/ui-kit/form/shared/BaseSelectInput/SelectInput'

import styles from './Select.module.scss'

type SelectProps<T extends number | string = string> = {
  /** Name of the input. Used for identifying it in an uncontrolled form, and for referencing the error */
  name: string
  className?: string
  required?: boolean
  disabled?: boolean
  label: string
  onChange?: React.InputHTMLAttributes<HTMLSelectElement>['onChange']
  onBlur?: React.FocusEventHandler<HTMLSelectElement>
  /** Option displayed if no option of the option list is selected */
  defaultOption?: SelectOption<T> | null
  options: SelectOption<T>[]
  /**
   * Type of required indicator. If it is a symbol, the signification of that symbol must be described somewhere else.
   */
  requiredIndicator?: 'symbol' | 'explicit' | null
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
      required = false,
      disabled,
      label,
      onChange,
      onBlur,
      error,
      requiredIndicator = 'symbol',
      value,
      ariaLabel,
    }: SelectProps<string | number>,
    ref: ForwardedRef<HTMLSelectElement>
  ): JSX.Element => {
    const fieldId = useId()
    const errorId = useId()

    return (
      <div className={classNames(styles['select'], className)}>
        <div className={styles['select-field']}>
          <FieldHeader
            label={label}
            inputId={fieldId}
            hasRequiredIndicator={required && requiredIndicator === 'symbol'}
          />
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
            aria-describedby={error ? errorId : undefined}
            ref={ref}
            id={fieldId}
            aria-label={ariaLabel}
          />
        </div>
        <FieldFooter error={error} errorId={errorId} />
      </div>
    )
  }
)

Select.displayName = 'Select'
