import cn from 'classnames'
import React, { ChangeEvent } from 'react'

import fullRightIcon from 'icons/full-right.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import { PhoneCodeSelectOption } from '../types'

import styles from './CountryCodeSelect.module.scss'

interface CountryCodeSelectProps {
  disabled: boolean
  options: PhoneCodeSelectOption[]
  className?: string
  value: string
  onChange: (event: ChangeEvent<HTMLSelectElement>) => void
}

export const CountryCodeSelect = ({
  disabled,
  options,
  className,
  value,
  onChange,
}: CountryCodeSelectProps) => {
  return (
    <div className={cn(styles['select-input-wrapper'], className)}>
      <SvgIcon
        src={fullRightIcon}
        alt=""
        className={cn(styles['select-input-icon'], {
          [styles['select-input-icon-disabled'] ?? '']: disabled,
        })}
        width="16"
      />
      <select
        className={styles['select-input']}
        id="countryCode"
        disabled={disabled}
        value={value}
        onChange={onChange}
        autoComplete="tel-country-code"
      >
        {options.map((option) => (
          <option key={option.value} value={option.value} label={option.label}>
            {option.label}
          </option>
        ))}
      </select>
    </div>
  )
}
