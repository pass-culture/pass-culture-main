import React from 'react'
import PropTypes from 'prop-types'
import { Field } from 'react-final-form'

import FormError from '../FormError'
import InputLabel from '../InputLabel'
import { isEmpty } from '../../../utils/strings'

const DEFAULT_REQUIRED_ERROR = 'Ce champ est requis'

const validateRequiredField = value => {
  if (value && !isEmpty(value)) return undefined
  return DEFAULT_REQUIRED_ERROR
}

const EmailField = ({
  autoComplete,
  className,
  disabled,
  id,
  label,
  name,
  placeholder,
  required,
  sublabel,
}) => {
  const validateFunc =
    required && typeof required === 'function'
      ? required
      : (required && validateRequiredField) || undefined
  return (
    <Field
      name={name}
      render={({ input, meta }) => (
        <p className={`${className}`}>
          <label
            className="pc-final-form-text"
            htmlFor={id || name}
          >
            {label && (
              <InputLabel
                label={label}
                required={required}
                sublabel={sublabel}
              />
            )}
            <span className="pc-final-form-inner">
              <input
                {...input}
                autoComplete={autoComplete ? 'on' : 'off'}
                className="pc-final-form-input is-block"
                disabled={disabled}
                id={id || name} // cast to boolean
                placeholder={placeholder}
                required={!!required}
                type="email"
              />
            </span>
            <FormError
              id={`${id || name}-error`}
              meta={meta}
            />
          </label>
        </p>
      )}
      validate={validateFunc || undefined}
    />
  )
}

EmailField.defaultProps = {
  autoComplete: false,
  className: '',
  disabled: false,
  id: null,
  label: '',
  placeholder: 'Identifiant (email)',
  required: false,
  sublabel: null,
}

EmailField.propTypes = {
  autoComplete: PropTypes.bool,
  className: PropTypes.string,
  disabled: PropTypes.bool,
  id: PropTypes.string,
  label: PropTypes.string,
  name: PropTypes.string.isRequired,
  placeholder: PropTypes.string,
  required: PropTypes.oneOfType([PropTypes.bool, PropTypes.func]),
  sublabel: PropTypes.string,
}

export default EmailField
