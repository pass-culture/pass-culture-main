/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import PropTypes from 'prop-types'
import { Field } from 'react-final-form'

import { FormError } from '../FormError'
import { validatePasswordField } from '../validators/validatePasswordField'

export class PasswordField extends React.PureComponent {
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
        : (required && validatePasswordField(name)) || undefined
    return (
      <Field
        name={name}
        // fallback to form validator
        // si le champs n'est pas marqué comme requis
        validate={validateFunc || undefined}
        render={({ input, meta }) => (
          <p className={`${className}`}>
            <label htmlFor={name} className="pc-final-form-password">
              {label && (
                <span className="pc-final-form-label">
                  <span>{label}</span>
                  {required && (
                    <span className="pc-final-form-asterisk">*</span>
                  )}
                </span>
              )}
              <span className="pc-final-form-inner">
                <input
                  {...input}
                  id={name}
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
                    className={`icon-eye${status} fs22`}
                    title=""
                  />
                </button>
              </span>
              <FormError meta={meta} />
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
  label: 'Saisissez Votre mot de passe',
  placeholder: '',
  required: false,
}

PasswordField.propTypes = {
  autoComplete: PropTypes.bool,
  className: PropTypes.string,
  disabled: PropTypes.bool,
  label: PropTypes.string,
  name: PropTypes.string.isRequired,
  placeholder: PropTypes.string,
  required: PropTypes.oneOfType([PropTypes.bool, PropTypes.func]),
}

export default PasswordField
