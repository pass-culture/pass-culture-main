import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import { Field } from 'react-final-form'

import FormError from '../FormError'
import InputLabel from '../InputLabel'
import { validatePasswordField } from '../validators'
import hasErrorMessage from '../utils/hasErrorMessage'

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
    const status = hidden ? '' : '-close'
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
            <span
              aria-hidden
              className={`icon-legacy-eye${status}`}
              title="Afficher/Masquer le mot de passe"
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
