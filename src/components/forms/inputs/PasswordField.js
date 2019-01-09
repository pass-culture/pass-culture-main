/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import PropTypes from 'prop-types'
import { Field } from 'react-final-form'

import FormError from '../FormError'
import InputHelp from '../InputHelp'
import InputLabel from '../InputLabel'
import { validatePasswordField } from '../validators'

class PasswordField extends React.PureComponent {
  constructor(props) {
    super(props)
    this.state = { hidden: true }
  }

  onToggleVivisbility = () => {
    this.setState(prev => ({ hidden: !prev.hidden }))
  }

  render() {
    const {
      autoComplete,
      className,
      disabled,
      help,
      id,
      label,
      name,
      placeholder,
      required,
    } = this.props
    const { hidden } = this.state
    const status = hidden ? '' : '-close'
    const inputType = hidden ? 'password' : 'text'
    const validateFunc =
      required && typeof required === 'function'
        ? required
        : (required && validatePasswordField) || undefined
    return (
      <Field
        name={name}
        // fallback to form validator
        // si le champs n'est pas marqué comme requis
        validate={validateFunc || undefined}
        render={({ input, meta }) => (
          <p className={`${className}`}>
            <label htmlFor={id || name} className="pc-final-form-password">
              {label && <InputLabel label={label} required={required} />}
              {help && <InputHelp label={help} />}
              <span className="pc-final-form-inner">
                <input
                  {...input}
                  id={id || name}
                  type={inputType}
                  disabled={disabled}
                  required={!!required} // cast to boolean
                  placeholder={placeholder}
                  autoComplete={autoComplete ? 'on' : 'off'}
                  className="pc-final-form-input"
                />

                <button
                  type="button"
                  onClick={this.onToggleVivisbility}
                  className="no-border no-outline no-background mx12 flex-0 is-primary-text"
                >
                  <span
                    aria-hidden
                    className={`icon-legacy-eye${status} fs22`}
                    title="Afficher/Masquer le mot de passe"
                  />
                </button>
              </span>
              <FormError id={`${id || name}-error`} meta={meta} />
            </label>
          </p>
        )}
      />
    )
  }
}

PasswordField.defaultProps = {
  autoComplete: false,
  className: '',
  disabled: false,
  help: null,
  id: null,
  label: 'Saisissez Votre mot de passe',
  placeholder: '',
  required: false,
}

PasswordField.propTypes = {
  autoComplete: PropTypes.bool,
  className: PropTypes.string,
  disabled: PropTypes.bool,
  help: PropTypes.string,
  id: PropTypes.string,
  label: PropTypes.string,
  name: PropTypes.string.isRequired,
  placeholder: PropTypes.string,
  required: PropTypes.oneOfType([PropTypes.bool, PropTypes.func]),
}

export default PasswordField
