import PropTypes from 'prop-types'
import React from 'react'

import { FormError } from '../../../../forms'
import { isEmpty } from '../../../../../utils/strings'
import { PasswordField } from '../../../../forms/inputs'
import { validateMatchingFields } from '../../../../forms/validators'
import withProfileForm from '../withProfileForm'

const ERROR_OLD_PASSWORD = "L'ancien mot de passe est manquant."

export class UserPasswordField extends React.PureComponent {
  buildOldPasswordLabel = () => value =>
    value && !isEmpty(value) ? undefined : ERROR_OLD_PASSWORD

  validateNewPassword = () => (newPasswordConfirm, formvalues) => {
    const { newPassword } = formvalues
    return validateMatchingFields(newPasswordConfirm, newPassword)
  }

  render() {
    const { formErrors, isLoading } = this.props
    return (
      <div className="pc-scroll-container">
        <div className="py30 px12 flex-1">
          <PasswordField
            disabled={isLoading}
            label="Saisissez votre mot de passe actuel"
            name="oldPassword"
            required={this.buildOldPasswordLabel()}
          />
          <PasswordField
            className="mt36"
            disabled={isLoading}
            label="Saisissez votre nouveau mot de passe"
            name="newPassword"
            required
          />
          <PasswordField
            className="mt36"
            disabled={isLoading}
            label="Confirmez votre nouveau mot de passe"
            name="newPasswordConfirm"
            required={this.validateNewPassword()}
          />
          {formErrors && <FormError customMessage={formErrors} />}
        </div>
      </div>
    )
  }
}

UserPasswordField.defaultProps = {
  formErrors: false,
}

UserPasswordField.propTypes = {
  formErrors: PropTypes.oneOfType([
    PropTypes.array,
    PropTypes.bool,
    PropTypes.string,
  ]),
  isLoading: PropTypes.bool.isRequired,
}

export default withProfileForm(
  UserPasswordField,
  {
    routeMethod: 'POST',
    routePath: 'users/current/change-password',
  },
  null
)
