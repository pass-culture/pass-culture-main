import cn from 'classnames'
import { ComponentProps } from 'react'

import { SelectOption } from 'commons/custom_types/form'
import fullDownIcon from 'icons/full-down.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './Select.module.scss'

export enum SelectInputVariant {
  FILTER = 'filter',
  FORM = 'form',
}

interface SelectInputProps extends ComponentProps<'select'> {
  name: string
  defaultOption?: SelectOption | null
  options: SelectOption[]
  hasError?: boolean
  hasDescription?: boolean
  value: string
  variant?: SelectInputVariant
}

export const SelectInput = ({
  hasError = false,
  hasDescription = false,
  defaultOption = null,
  name,
  disabled,
  options,
  className,
  variant,
  ...field
}: SelectInputProps): JSX.Element => (
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
