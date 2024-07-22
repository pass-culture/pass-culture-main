import cn from 'classnames'
import React, { ComponentProps } from 'react'

import { SelectOption } from 'custom_types/form'
import strokeDownIcon from 'icons/stroke-down.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './Select.module.scss'

interface SelectInputProps extends ComponentProps<'select'> {
  name: string
  defaultOption?: SelectOption | null
  options: SelectOption[]
  hasError?: boolean
  filterVariant?: boolean
  hasDescription?: boolean
  value: string
}

export const SelectInput = ({
  hasError = false,
  filterVariant,
  hasDescription = false,
  defaultOption = null,
  name,
  disabled,
  options,
  className,
  ...field
}: SelectInputProps): JSX.Element => (
  <div
    className={cn(styles['select-input-wrapper'], {
      [styles['has-description'] ?? '']: hasDescription,
    })}
  >
    <select
      aria-invalid={hasError}
      {...(hasError ? { 'aria-describedby': `error-${name}` } : {})}
      className={cn(styles['select-input'], className, {
        [styles['has-error'] ?? '']: hasError,
        [styles['has-description'] ?? '']: hasDescription,
        [styles['select-input-placeholder'] ?? '']: field.value === '',
        [styles['filter-variant'] ?? '']: filterVariant,
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
        [styles['filter-variant'] ?? '']: filterVariant,
      })}
    >
      <SvgIcon src={strokeDownIcon} alt="" width="0" />
    </div>
  </div>
)
