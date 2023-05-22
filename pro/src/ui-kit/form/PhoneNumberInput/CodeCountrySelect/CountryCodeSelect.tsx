import cn from 'classnames'
import React, { ChangeEvent } from 'react'

import { ReactComponent as Down } from 'icons/ico-mini-arrow-right.svg'

import { PhoneCodeSelectOption } from '../types'

import styles from './CountryCodeSelect.module.scss'

interface CountryCodeSelectProps {
  disabled: boolean
  options: PhoneCodeSelectOption[]
  className?: string
  value: string
  onChange: (event: ChangeEvent<HTMLSelectElement>) => void
}

const CountryCodeSelect = ({
  disabled,
  options,
  className,
  value,
  onChange,
}: CountryCodeSelectProps) => {
  return (
    <div className={cn(styles['select-input-wrapper'], className)}>
      <Down
        className={cn(styles['select-input-icon'], {
          [styles['select-input-icon-disabled']]: disabled,
        })}
      />
      <select
        className={styles['select-input']}
        id="countryCode"
        disabled={disabled}
        value={value}
        onChange={onChange}
      >
        {options.map(option => (
          <option key={option.value} value={option.value} label={option.label}>
            {option.label}
          </option>
        ))}
      </select>
    </div>
  )
}

export default CountryCodeSelect
