import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { Field } from 'react-final-form'

import FormError from '../FormError'
import InputLabel from '../InputLabel'
import isEmpty from '../../../utils/strings/isEmpty'
import hasErrorMessage from '../utils/hasErrorMessage'

const DEFAULT_REQUIRED_ERROR = 'Ce champ est requis'

const validateRequiredField = value => {
  if (value && !isEmpty(value)) return undefined
  return DEFAULT_REQUIRED_ERROR
}

class EmailField extends Component {
  renderField = ({ input, meta }) => {
    const { autoComplete, disabled, id, label, name, placeholder, required, sublabel } = this.props

    return (
      <label className="label-email-inner">
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
            id={id || name}
            placeholder={placeholder}
            required={!!required}
            type="email"
          />
        </div>
        <FormError meta={meta} />
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

EmailField.defaultProps = {
  autoComplete: false,
  disabled: false,
  id: null,
  placeholder: 'Identifiant (e-mail)',
  required: false,
  sublabel: null,
}

EmailField.propTypes = {
  autoComplete: PropTypes.bool,
  disabled: PropTypes.bool,
  id: PropTypes.string,
  label: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  placeholder: PropTypes.string,
  required: PropTypes.oneOfType([PropTypes.bool, PropTypes.func]),
  sublabel: PropTypes.string,
}

export default EmailField
