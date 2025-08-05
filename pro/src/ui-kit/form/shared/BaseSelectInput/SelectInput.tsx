import cn from 'classnames'
import { SelectOption } from 'commons/custom_types/form'
import fullDownIcon from 'icons/full-down.svg'
import { ComponentProps, ForwardedRef, forwardRef } from 'react'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './Select.module.scss'

enum SelectInputVariant {
  FILTER = 'filter',
  FORM = 'form',
}

interface SelectInputProps<T extends number | string = string>
  extends ComponentProps<'select'> {
  name: string
  defaultOption?: SelectOption<T> | null
  options: SelectOption<T>[]
  hasError?: boolean
  hasDescription?: boolean
  value?: string
  variant?: SelectInputVariant
}

export const SelectInput = forwardRef(
  (
    {
      hasError = false,
      hasDescription = false,
      defaultOption = null,
      name,
      disabled,
      options,
      className,
      variant,
      ...field
    }: SelectInputProps<number | string>,
    ref: ForwardedRef<HTMLSelectElement>
  ): JSX.Element => (
    <div
      className={cn(styles['select-input-wrapper'], {
        [styles['has-description']]: hasDescription,
      })}
    >
      <select
        aria-invalid={hasError}
        {...(hasError ? { 'aria-describedby': `error-${name}` } : {})}
        className={cn(styles['select-input'], className, {
          [styles['has-error']]: hasError,
          [styles['has-description']]: hasDescription,
          [styles['select-input-placeholder']]: field.value === '',
          [styles['filter-variant']]: variant === SelectInputVariant.FILTER,
          [styles['form-variant']]: variant === SelectInputVariant.FORM,
          [styles['has-value']]: !!field.value,
        })}
        disabled={disabled}
        id={name}
        name={name}
        {...field}
        ref={ref}
      >
        {defaultOption && (
          <option value={defaultOption.value}>{defaultOption.label}</option>
        )}
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      <div
        className={cn(styles['select-input-icon'], {
          [styles['filter-variant']]: variant === SelectInputVariant.FILTER,
        })}
      >
        <SvgIcon src={fullDownIcon} alt="" />
      </div>
    </div>
  )
)

SelectInput.displayName = 'SelectInput'
