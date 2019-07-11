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
      sublabel,
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
        render={({ input, meta }) => (
          <p className={`${className}`}>
            <label
              className="pc-final-form-password"
              htmlFor={id || name}
            >
              {label && (
                <InputLabel
                  label={label}
                  required={required}
                  sublabel={sublabel}
                />
              )}
              {help && <InputHelp label={help} />}
              <span className="pc-final-form-inner">
                <input
                  {...input}
                  autoComplete={autoComplete ? 'on' : 'off'}
                  className="pc-final-form-input"
                  disabled={disabled}
                  id={id || name} // cast to boolean
                  placeholder={placeholder}
                  required={!!required}
                  type={inputType}
                />

                <button
                  className="no-border no-outline no-background mx12 flex-0 is-primary-text"
                  onClick={this.onToggleVivisbility}
                  type="button"
                >
                  <span
                    aria-hidden
                    className={`icon-legacy-eye${status} fs22`}
                    title="Afficher/Masquer le mot de passe"
                  />
                </button>
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
  sublabel: null,
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
  sublabel: PropTypes.string,
}

export default PasswordField
