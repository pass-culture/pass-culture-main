import cn from 'classnames'
import React from 'react'

import { ReactComponent as Down } from './assets/down.svg'
import styles from './Select.module.scss'

type Option = {
  label: string
  value: string
}

interface ISelectInputProps {
  name: string
  options: Option[]
  disabled?: boolean
  hasError?: boolean
}

const SelectInput = ({
  hasError = false,
  name,
  disabled,
  options,
  ...field
}: ISelectInputProps): JSX.Element => (
  <div className={styles['select-input-wrapper']}>
    <select
      aria-invalid={hasError}
      className={cn(styles['select-input'], {
        [styles['has-error']]: hasError,
      })}
      disabled={disabled}
      id={name}
      {...field}
    >
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
