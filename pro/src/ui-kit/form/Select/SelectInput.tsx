import cn from 'classnames'
import React, { ComponentProps } from 'react'

import { SelectOption } from 'custom_types/form'

import { ReactComponent as Down } from './assets/down.svg'
import styles from './Select.module.scss'

interface ISelectInputProps extends ComponentProps<'select'> {
  name: string
  defaultOption?: SelectOption | null
  options: SelectOption[]
  hasError?: boolean
  hasDescription?: boolean
  value: string
}

const SelectInput = ({
  hasError = false,
  hasDescription = false,
  defaultOption = null,
  name,
  disabled,
  options,
  ...field
}: ISelectInputProps): JSX.Element => (
  <div
    className={cn(styles['select-input-wrapper'], {
      [styles['has-description']]: hasDescription,
    })}
  >
    <select
      aria-invalid={hasError}
      {...(hasError ? { 'aria-describedby': `error-${name}` } : {})}
      className={cn(styles['select-input'], {
        [styles['has-error']]: hasError,
        [styles['has-description']]: hasDescription,
        [styles['select-input-placeholder']]:
          field.value === '' || field.value === null,
      })}
      disabled={disabled}
      id={name}
      {...field}
    >
      {defaultOption && (
        <option value={defaultOption.value}>{defaultOption.label}</option>
      )}
      {options.map(option => (
        <option key={option.value} value={option.value}>
          {option.label}
        </option>
      ))}
    </select>
    <div className={styles['select-input-icon']}>
      <Down />
    </div>
  </div>
)

export default SelectInput
