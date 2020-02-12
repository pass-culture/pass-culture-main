import PropTypes from 'prop-types'
import React, { forwardRef } from 'react'
import Icon from '../../../../layout/Icon/Icon'

const NOOP = () => {}

export const MesInformationsField = forwardRef(function MesInformationsField(props, ref) {
  const {
    disabled,
    errors,
    id,
    label,
    onBlur,
    onChange,
    maxLength,
    minLength,
    name,
    required,
    value,
  } = props

  return (
    <div className="mi-field">
      <label htmlFor={id}>
        {label}
      </label>
      <input
        aria-invalid={errors ? true : false}
        className="mi-field-input"
        disabled={disabled}
        id={id}
        maxLength={maxLength}
        minLength={minLength}
        name={name}
        onBlur={onBlur}
        onChange={onChange}
        ref={ref}
        required={required}
        type="text"
        value={value}
      />
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

MesInformationsField.defaultProps = {
  disabled: false,
  errors: null,
  maxLength: -1,
  minLength: 0,
  onBlur: NOOP,
  onChange: NOOP,
  required: false,
  value: '',
}

MesInformationsField.propTypes = {
  disabled: PropTypes.bool,
  errors: PropTypes.arrayOf(PropTypes.string),
  id: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
  maxLength: PropTypes.number,
  minLength: PropTypes.number,
  name: PropTypes.string.isRequired,
  onBlur: PropTypes.func,
  onChange: PropTypes.func,
  required: PropTypes.bool,
  value: PropTypes.string,
}
