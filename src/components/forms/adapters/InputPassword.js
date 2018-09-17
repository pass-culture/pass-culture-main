/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import PropTypes from 'prop-types'
// import { Field } from 'react-final-form'

class InputPassword extends React.PureComponent {
  constructor(props) {
    super(props)
    this.state = { hidden: true }
  }

  onFocusOut = () => {
    this.setState({ hidden: true })
  }

  onToggleVivisbility = () => {
    this.setState(prev => ({ hidden: !prev.hidden }))
  }

  render() {
    const {
      className,
      defaultValue,
      disabled,
      label,
      name,
      placeholder,
    } = this.props
    const { hidden } = this.state
    const status = hidden ? '-close' : ''
    const inputType = hidden ? 'password' : 'text'
    return (
      <p className={`fs19 ${className}`}>
        <label htmlFor={name} className="pc-form-label pc-form-password">
          {label && <span className="is-block">{label}</span>}
          <span className="inner flex-columns">
            <input
              id={name}
              type={inputType}
              disabled={disabled}
              onChange={() => {}}
              onFocusOut={this.onBlur}
              placeholder={placeholder}
              defaultValue={defaultValue}
              className="no-border no-outline is-block flex-1"
            />
            <button
              type="button"
              onClick={this.onToggleVivisbility}
              className="no-border no-outline no-background flex-0"
            >
              <span aria-hidden className={`icon-eye${status}`} title="" />
            </button>
          </span>
        </label>
      </p>
    )
  }
}

InputPassword.defaultProps = {
  className: '',
  defaultValue: '',
  disabled: false,
  label: PropTypes.string,
  placeholder: 'Veuillez saisir une valeur',
}

InputPassword.propTypes = {
  className: PropTypes.string,
  defaultValue: PropTypes.string,
  disabled: PropTypes.bool,
  label: PropTypes.string,
  name: PropTypes.string.isRequired,
  placeholder: PropTypes.string,
}

export default InputPassword
