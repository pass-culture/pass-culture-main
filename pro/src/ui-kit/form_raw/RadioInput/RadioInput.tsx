import cn from 'classnames'
import React from 'react'

interface RadioInputProps {
  checked: boolean
  disabled?: boolean
  error?: string | null
  label: string
  name: string
  onChange: (event: React.ChangeEvent<HTMLInputElement>) => void
  subLabel?: string | null
  value: string
}

export const RadioInput = ({
  onChange,
  value,
  name,
  label,
  checked,
  disabled,
  subLabel,
  error,
}: RadioInputProps) => (
  <label className="input-radio">
    <input
      checked={checked}
      className={cn('input-radio-input', { error })}
      disabled={disabled}
      name={name}
      onChange={onChange}
      type="radio"
      value={value}
    />
    <span className={`input-radio-label ${disabled ? 'disabled' : ''}`}>
      {label}
      {subLabel && (
        <span className={`input-radio-sub-label ${disabled ? 'disabled' : ''}`}>
          {subLabel}
        </span>
      )}
    </span>
  </label>
)
