import cn from 'classnames'
import React from 'react'

import { ReactComponent as Down } from './assets/down.svg'
import styles from './Select.module.scss'

type Option = {
  value: string
  label: string
}

interface ISelectInputProps {
  name: string
  options: Option[]
  disabled?: boolean
  hasError?: boolean
}

const SelectInput = ({
  hasError = false,
  disabled,
  options,
  ...field
}: ISelectInputProps): JSX.Element => (
  <div className={styles['select-input-wrapper']}>
    <select
      className={cn(styles['select-input'], {
        [styles['has-error']]: hasError,
      })}
      disabled={disabled}
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
