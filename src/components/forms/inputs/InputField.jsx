import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { Field } from 'react-final-form'

import FormError from '../FormError'
import InputLabel from '../InputLabel'
import validateRequiredField from '../validators/validateRequiredField'
import hasErrorMessage from '../utils/hasErrorMessage'

class InputField extends Component {
  renderField = ({ input, meta }) => {
    const {
      autoComplete,
      disabled,
      label,
      name,
      placeholder,
      required,
      sublabel,
      theme,
    } = this.props

    return (
      <label className="label-text-inner">
        <InputLabel
          label={label}
          required={required}
          sublabel={sublabel}
        />
        <div className={`input-inner${hasErrorMessage(meta)}`}>
          <input
            {...input}
            autoComplete={autoComplete ? 'on' : 'off'}
            className="form-input"
            disabled={disabled}
            id={name}
            placeholder={placeholder}
            required={!!required}
            type="text"
          />
        </div>
        <FormError
          meta={meta}
          theme={theme}
        />
      </label>
    )
  }

  render() {
    const { name, required } = this.props
    const validateFunc =
      required && typeof required === 'function'
        ? required
        : (required && validateRequiredField) || undefined

    return (<Field
      name={name}
      render={this.renderField}
      validate={validateFunc || undefined}
            />)
  }
}

InputField.defaultProps = {
  autoComplete: false,
  disabled: false,
  placeholder: 'Veuillez saisir une valeur',
  required: false,
  sublabel: null,
  theme: 'white',
}

InputField.propTypes = {
  autoComplete: PropTypes.bool,
  disabled: PropTypes.bool,
  label: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  placeholder: PropTypes.string,
  required: PropTypes.oneOfType([PropTypes.bool, PropTypes.func]),
  sublabel: PropTypes.string,
  theme: PropTypes.string,
}

export default InputField
