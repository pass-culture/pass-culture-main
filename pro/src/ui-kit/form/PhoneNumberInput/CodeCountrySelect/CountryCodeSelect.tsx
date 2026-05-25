import cn from 'classnames'
import type { ChangeEvent, FocusEvent } from 'react'

import fullRightIcon from '@/icons/full-right.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import type { CountryCodeSelectOption } from '../PhoneNumberInput'
import styles from './CountryCodeSelect.module.scss'

interface CountryCodeSelectProps {
  id: string
  disabled: boolean
  options: CountryCodeSelectOption[]
  className?: string
  value: string
  onChange: (event: ChangeEvent<HTMLSelectElement>) => void
  onBlur: (event: FocusEvent<HTMLSelectElement>) => void
}

export const CountryCodeSelect = ({
  id,
  disabled,
  options,
  className,
  value,
  onChange,
  onBlur,
}: CountryCodeSelectProps) => {
  return (
    <div className={cn(styles['select-input-wrapper'], className)}>
      <SvgIcon
        src={fullRightIcon}
        alt=""
        className={cn(styles['select-input-icon'], {
          [styles['select-input-icon-disabled']]: disabled,
        })}
        width="16"
      />
      <select
        className={styles['select-input']}
        id={id}
        disabled={disabled}
        value={value}
        onChange={onChange}
        onBlur={onBlur}
        autoComplete="tel-country-code"
        aria-label="Indicatifs pays"
      >
        {options.map((option) => (
          <option key={option.value} value={option.value} label={option.value}>
            {option.value}
          </option>
        ))}
      </select>
    </div>
  )
}
