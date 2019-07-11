import React from 'react'

const Select = ({
  className,
  defaultLabel,
  extraClass,
  onOptionClick,
  options,
  value,
}) => {
  return (
    <select
      className={className || 'select'}
      onChange={onOptionClick}
      value={value || defaultLabel}
    >
      <option
        disabled
        key={-1}
      >
        {defaultLabel}
      </option>
      {options.map(({ label, value }, index) => (
        <option
          key={index}
          value={value}
        >
          {label}
        </option>
      ))}
    </select>
  )
}

export default Select
