import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'

import Icon from '../../../../layout/Icon/Icon'

class EditPasswordField extends PureComponent {
  constructor(props) {
    super(props)

    this.state = {
      alt: 'Afficher le mot de passe',
      iconName: 'ico-eye-open',
      inputType: 'password',
    }
  }

  handleToggleVisibility = () => {
    this.setState(prev =>
      prev.inputType === 'password'
        ? {
            alt: 'Masquer le mot de passe',
            iconName: 'ico-eye-close',
            inputType: 'text',
          }
        : {
            alt: 'Afficher le mot de passe',
            iconName: 'ico-eye-open',
            inputType: 'password',
          }
    )
  }

  render() {
    const { errors, inputRef, label, onChange, placeholder, value } = this.props
    const { alt, iconName, inputType } = this.state

    return (
      <div className="mi-field">
        <label>
          {label}
          <input
            aria-invalid={errors ? true : false}
            className="mi-field-input"
            minLength="12"
            onChange={onChange}
            placeholder={placeholder}
            ref={inputRef}
            required
            type={inputType}
            value={value}
          />
          <button
            onClick={this.handleToggleVisibility}
            type="button"
          >
            <Icon
              alt={alt}
              svg={iconName}
            />
          </button>
        </label>
        <div
          aria-live="assertive"
          aria-relevant="all"
        >
          {errors &&
            errors.map(error => (
              <div
                className="mi-field-error"
                key={error}
              >
                <Icon svg="ico-error" />
                <p>
                  {error}
                </p>
              </div>
            ))}
        </div>
      </div>
    )
  }
}

EditPasswordField.defaultProps = {
  errors: null,
  placeholder: '',
}

EditPasswordField.propTypes = {
  errors: PropTypes.arrayOf(PropTypes.string),
  inputRef: PropTypes.shape().isRequired,
  label: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
  placeholder: PropTypes.string,
  value: PropTypes.string.isRequired,
}

export default EditPasswordField
