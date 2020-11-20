import React, { Fragment } from 'react'

const BasicInput = props => {
  const {
    autoComplete,
    checked,
    className,
    disabled,
    id,
    name,
    onBlur,
    onChange,
    readOnly,
    renderInfo,
    required,
    type,
    size,
    value,
    min,
    step,
    placeholder,
  } = props

  return (
    <Fragment>
      <input
        aria-describedby={props['aria-describedby']}
        autoComplete={autoComplete}
        checked={checked}
        className={className || `input is-${size}`}
        disabled={disabled}
        id={id}
        min={min}
        name={name}
        onBlur={onBlur}
        onChange={onChange}
        placeholder={placeholder}
        readOnly={readOnly}
        required={required}
        step={step}
        type={type}
        value={value}
      />
      {renderInfo && renderInfo()}
    </Fragment>
  )
}

export default BasicInput
