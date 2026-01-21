import cn from 'classnames'
import { type ForwardedRef, forwardRef, useId } from 'react'

import type { SelectOption } from '@/commons/custom_types/form'
import { FieldFooter } from '@/design-system/common/FieldFooter/FieldFooter'
import { FieldHeader } from '@/design-system/common/FieldHeader/FieldHeader'
import type { RequiredIndicator } from '@/design-system/common/types'
import fullDownIcon from '@/icons/full-down.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

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
  /** What type of required indicator is displayed */
  requiredIndicator?: RequiredIndicator
  error?: string
  value?: string
  ariaLabel?: string
}

export const Select = forwardRef(
  (
    {
      name,
      label,
      options,
      defaultOption = null,
      required = false,
      disabled,
      error,
      requiredIndicator = 'symbol',
      className,
      ariaLabel,
      value,
      onChange,
      onBlur,
    }: SelectProps<string | number>,
    ref: ForwardedRef<HTMLSelectElement>
  ): JSX.Element => {
    const fieldId = useId()
    const errorId = useId()

    return (
      <div className={cn(styles['select'], className)}>
        <div className={styles['select-field']}>
          <FieldHeader
            label={label}
            fieldId={fieldId}
            required={required}
            requiredIndicator={requiredIndicator}
          />

          <div className={styles['select-input-wrapper']}>
            <select
              ref={ref}
              id={fieldId}
              name={name}
              disabled={disabled}
              value={value}
              aria-label={ariaLabel}
              aria-required={required}
              aria-invalid={Boolean(error)}
              aria-describedby={error ? errorId : undefined}
              className={cn(styles['select-input'], {
                [styles['has-error']]: Boolean(error),
                [styles['select-input-placeholder']]: value === '',
                [styles['has-value']]: !!value,
              })}
              onBlur={onBlur}
              onChange={onChange}
            >
              {defaultOption && (
                <option value={defaultOption.value}>
                  {defaultOption.label}
                </option>
              )}
              {options.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>

            <div className={styles['select-input-icon']}>
              <SvgIcon src={fullDownIcon} alt="" />
            </div>
          </div>
        </div>

        <FieldFooter error={error} errorId={errorId} />
      </div>
    )
  }
)

Select.displayName = 'Select'
