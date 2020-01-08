import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import { Field } from 'react-final-form'

import FormError from '../FormError'
import hasErrorMessage from '../utils/hasErrorMessage'
import Icon from '../../layout/Icon/Icon'
import InputLabel from '../InputLabel'
import validatePasswordField from '../validators/validatePasswordField'

class PasswordField extends PureComponent {
  constructor(props) {
    super(props)
    this.state = { hidden: true }
  }

  handleOnToggleVisibility = () => {
    this.setState(prev => ({ hidden: !prev.hidden }))
  }

  renderField = ({ input, meta }) => {
    const { autoComplete, disabled, id, label, name, placeholder, required, sublabel } = this.props
    const { hidden } = this.state
    const status = hidden ? 'open' : 'close'
    const inputType = hidden ? 'password' : 'text'

    return (
      <label className="label-password-inner">
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
            type={inputType}
          />
          <button
            className="no-background mx12 flex-0 is-primary-text"
            onClick={this.handleOnToggleVisibility}
            type="button"
          >
            <Icon
              alt="Afficher/Masquer le mot de passe"
              svg={`ico-eye-${status}`}
            />
          </button>
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
        : (required && validatePasswordField) || undefined

    return (
      <Field
        name={name}
        // fallback to form validator
        // si le champs n'est pas marqué comme requis
        render={this.renderField}
        validate={validateFunc || undefined}
      />
    )
  }
}

PasswordField.defaultProps = {
  autoComplete: false,
  disabled: false,
  id: null,
  placeholder: '',
  required: false,
  sublabel: null,
}

PasswordField.propTypes = {
  autoComplete: PropTypes.bool,
  disabled: PropTypes.bool,
  id: PropTypes.string,
  label: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  placeholder: PropTypes.string,
  required: PropTypes.oneOfType([PropTypes.bool, PropTypes.func]),
  sublabel: PropTypes.string,
}

export default PasswordField
