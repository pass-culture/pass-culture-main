import PropTypes from 'prop-types'
import React, { Fragment } from 'react'

import FormError from '../../../../forms/FormError'
import isEmpty from '../../../../../utils/strings/isEmpty'
import PasswordField from '../../../../forms/inputs/PasswordField'
import validateMatchingFields from '../../../../forms/validators/validateMatchingFields'
import withProfileForm from '../withProfileForm'

const ERROR_OLD_PASSWORD = 'L’ancien mot de passe est manquant.'

export class UserPasswordField extends React.PureComponent {
  buildOldPasswordLabel = () => value => (value && !isEmpty(value) ? undefined : ERROR_OLD_PASSWORD)

  validateNewPassword = () => (newPasswordConfirm, formvalues) => {
    const { newPassword } = formvalues

    return validateMatchingFields(newPasswordConfirm, newPassword)
  }

  render() {
    const { formErrors, isLoading } = this.props

    return (
      <Fragment>
        <PasswordField
          disabled={isLoading}
          label="Saisissez votre mot de passe actuel"
          name="oldPassword"
          required={this.buildOldPasswordLabel()}
        />
        <PasswordField
          disabled={isLoading}
          label="Saisissez votre nouveau mot de passe"
          name="newPassword"
          required
        />
        <PasswordField
          disabled={isLoading}
          label="Confirmez votre nouveau mot de passe"
          name="newPasswordConfirm"
          required={this.validateNewPassword()}
        />
        {formErrors && <FormError customMessage={formErrors} />}
      </Fragment>
    )
  }
}

UserPasswordField.defaultProps = {
  formErrors: false,
}

UserPasswordField.propTypes = {
  formErrors: PropTypes.oneOfType([PropTypes.array, PropTypes.bool, PropTypes.string]),
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
