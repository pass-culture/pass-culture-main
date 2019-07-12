import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { Field } from 'react-final-form'

import FormError from '../FormError'
import InputLabel from '../InputLabel'
import { validateRequiredField } from '../validators'

class InputField extends Component {
  renderField = ({ input, meta }) => {
    const {
      autoComplete,
      className,
      disabled,
      label,
      name,
      placeholder,
      required,
      sublabel,
    } = this.props

    return (
      <p className={`${className}`}>
        <label
          className="pc-final-form-text"
          htmlFor={name}
        >
          {label && <InputLabel
            label={label}
            required={required}
            sublabel={sublabel}
                    />}
          <span className="pc-final-form-inner">
            <input
              {...input}
              autoComplete={autoComplete ? 'on' : 'off'}
              className="pc-final-form-input is-block"
              disabled={disabled}
              id={name} // cast to boolean
              placeholder={placeholder}
              required={!!required}
              type="text"
            />
          </span>
          <FormError meta={meta} />
        </label>
      </p>
    )
  }

  render() {
    const {
      name,
      required,
    } = this.props
    const validateFunc =
      required && typeof required === 'function'
        ? required
        : (required && validateRequiredField) || undefined
    return (
      <Field
        name={name}
        render={this.renderField}
        validate={validateFunc || undefined}
      />
    )
  }
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
