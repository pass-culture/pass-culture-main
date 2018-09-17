/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import PropTypes from 'prop-types'
import { Field } from 'react-final-form'

import InputPassword from '../adapters/InputPassword'

const renderField = options => <InputPassword {...options} />

export class PasswordField extends React.PureComponent {
  renderField() {
    const {
      label,
      name,
      defaultValue,
      disabled,
      fieldClassName,
      placeholder,
    } = this.props
    const options = {
      className: fieldClassName,
      defaultValue,
      disabled,
      label,
      name: `${name}`,
      placeholder,
    }
    return renderField(options)
  }

  renderConfirmField() {
    const {
      labelConfirm,
      name,
      disabled,
      fieldClassName,
      placeholder,
    } = this.props
    const options = {
      className: `${fieldClassName} mt12`,
      disabled,
      label: labelConfirm,
      name: `${name}-confirm`,
      placeholder,
    }
    return renderField(options)
  }

  render() {
    const { className, disabled, name, single } = this.props
    const cssclass = (single && className) || `${className} with-confirm`
    return (
      <Field
        name={name}
        disabled={disabled}
        render={() => (
          <div className={cssclass}>
            {this.renderField()}
            {!single && this.renderConfirmField()}
          </div>
        )}
      />
    )
  }
}

PasswordField.defaultProps = {
  className: '',
  defaultValue: '',
  disabled: false,
  fieldClassName: '',
  label: 'Votre mot de passe',
  labelConfirm: 'Confirmer votre mot de passe',
  placeholder: '',
  single: false,
}

PasswordField.propTypes = {
  className: PropTypes.string,
  defaultValue: PropTypes.string,
  disabled: PropTypes.bool,
  fieldClassName: PropTypes.string,
  label: PropTypes.string,
  labelConfirm: PropTypes.string,
  name: PropTypes.string.isRequired,
  placeholder: PropTypes.string,
  single: PropTypes.bool,
}

export default PasswordField
