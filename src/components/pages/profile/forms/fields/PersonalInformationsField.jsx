import PropTypes from 'prop-types'
import React, { forwardRef } from 'react'

import Icon from '../../../../layout/Icon/Icon'

const NOOP = () => {}

const PersonalInformationsField = forwardRef(function PersonalInformationsField(props, ref) {
  const { disabled, errors, label, onChange, maxLength, minLength, name, required, value } = props

  return (
    <div className="mi-field">
      <label>
        {label}
        <input
          aria-invalid={errors ? true : false}
          className="mi-field-input"
          disabled={disabled}
          maxLength={maxLength}
          minLength={minLength}
          name={name}
          onChange={onChange}
          ref={ref}
          required={required}
          type="text"
          value={value}
        />
      </label>
      <div
        aria-live="assertive"
        aria-relevant="all"
      >
        {errors &&
          errors.map(error => (
            <div
              className="mi-field-error"
              key={error}
            >
              <Icon svg="ico-error" />
              <p>
                {error}
              </p>
            </div>
          ))}
      </div>
    </div>
  )
})

PersonalInformationsField.defaultProps = {
  disabled: false,
  errors: null,
  maxLength: -1,
  minLength: 0,
  onChange: NOOP,
  required: false,
  value: '',
}

PersonalInformationsField.propTypes = {
  disabled: PropTypes.bool,
  errors: PropTypes.arrayOf(PropTypes.string),
  label: PropTypes.string.isRequired,
  maxLength: PropTypes.number,
  minLength: PropTypes.number,
  name: PropTypes.string.isRequired,
  onChange: PropTypes.func,
  required: PropTypes.bool,
  value: PropTypes.string,
}

export default PersonalInformationsField
