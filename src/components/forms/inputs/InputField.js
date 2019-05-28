/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import PropTypes from 'prop-types'
import { Field } from 'react-final-form'

import FormError from '../FormError'
import InputLabel from '../InputLabel'
import { validateRequiredField } from '../validators'

const InputField = ({
  autoComplete,
  className,
  disabled,
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
      validate={validateFunc || undefined}
      render={({ input, meta }) => (
        <p className={`${className}`}>
          <label htmlFor={name} className="pc-final-form-text">
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
                id={name}
                type="text"
                disabled={disabled}
                required={!!required} // cast to boolean
                placeholder={placeholder}
                autoComplete={autoComplete ? 'on' : 'off'}
                className="pc-final-form-input is-block"
              />
            </span>
            <FormError meta={meta} />
          </label>
        </p>
      )}
    />
  )
}

InputField.defaultProps = {
  autoComplete: false,
  className: '',
  disabled: false,
  label: '',
  placeholder: 'Veuillez saisir une valeur',
  required: false,
  sublabel: null,
}

InputField.propTypes = {
  autoComplete: PropTypes.bool,
  className: PropTypes.string,
  disabled: PropTypes.bool,
  label: PropTypes.string,
  name: PropTypes.string.isRequired,
  placeholder: PropTypes.string,
  required: PropTypes.oneOfType([PropTypes.bool, PropTypes.func]),
  sublabel: PropTypes.string,
}

export default InputField
