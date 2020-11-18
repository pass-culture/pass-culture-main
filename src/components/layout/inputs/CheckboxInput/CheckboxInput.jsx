import PropTypes from 'prop-types'
import React from 'react'

export const CheckboxInput = ({
  onChange,
  name,
  label,
  checked,
  labelAttributes,
  className,
  hiddenLabel,
  ...attributes
}) => {
  let inputClasses = className ? className.split(' ') : []
  inputClasses.push('input-checkbox')
  let textClasses = ['input-checkbox-label']
  if (hiddenLabel) {
    textClasses.push('label-hidden')
  }

  return (
    <label
      className="field field-checkbox"
      {...labelAttributes}
    >
      <input
        checked={checked}
        className={inputClasses.join(' ')}
        name={name}
        onChange={onChange}
        type="checkbox"
        {...attributes}
      />
      <span className={textClasses.join(' ')}>
        {label}
      </span>
    </label>
  )
}

CheckboxInput.defaultProps = {
  className: '',
  hiddenLabel: false,
  labelAttributes: {},
}

CheckboxInput.propTypes = {
  checked: PropTypes.bool.isRequired,
  className: PropTypes.string,
  hiddenLabel: PropTypes.bool,
  label: PropTypes.string.isRequired,
  labelAttributes: PropTypes.shape(),
  name: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
}
