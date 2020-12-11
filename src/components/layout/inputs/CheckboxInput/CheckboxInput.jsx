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
  subLabel,
  ...attributes
}) => {
  let inputClasses = className ? className.split(' ') : []
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
        {subLabel && (
          <span className="ic-sub-label">
            {subLabel}
          </span>
        )}
      </span>
    </label>
  )
}

CheckboxInput.defaultProps = {
  className: '',
  hiddenLabel: false,
  labelAttributes: {},
  subLabel: null,
}

CheckboxInput.propTypes = {
  checked: PropTypes.bool.isRequired,
  className: PropTypes.string,
  hiddenLabel: PropTypes.bool,
  label: PropTypes.string.isRequired,
  labelAttributes: PropTypes.shape(),
  name: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
  subLabel: PropTypes.string,
}
