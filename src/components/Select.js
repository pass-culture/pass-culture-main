import React from 'react'

const Select = ({ className,
  defaultLabel,
  extraClass,
  onOptionClick,
  options
}) => {
  return (
    <select className={className || 'select'}
      defaultValue={defaultLabel}
      onChange={onOptionClick}
    >
      <option key={-1} disabled>
        {defaultLabel}
      </option>
      {
        options.map(({ label, value }, index) => (
          <option key={index}
            value={value}
          >
            {label}
          </option>
        ))
      }
    </select>
  )
}

export default Select
