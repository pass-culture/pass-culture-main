import PropTypes from 'prop-types'
import React from 'react'

import { FormError } from '../../../../forms'
import { isEmpty } from '../../../../../utils/strings'
import { PasswordField } from '../../../../forms/inputs'
import { validateMatchingFields } from '../../../../forms/validators'
import withProfileForm from '../withProfileForm'

const ERROR_OLD_PASSWORD = "L'ancien mot de passe est manquant."

const initialValues = {
  newPassword: null,
  newPasswordConfirm: null,
  oldPassword: null,
}

class PasswordForm extends React.PureComponent {
  render() {
    const { formErrors, isLoading } = this.props
    return (
      <div className="pc-scroll-container">
        <div className="py30 px12 flex-1">
          <PasswordField
            required={value => {
              if (value && !isEmpty(value)) return undefined
              return ERROR_OLD_PASSWORD
            }}
            name="oldPassword"
            disabled={isLoading}
            label="Saisissez votre mot de passe actuel"
          />
          <PasswordField
            required
            className="mt36"
            name="newPassword"
            disabled={isLoading}
            label="Saisissez votre nouveau mot de passe"
          />
          <PasswordField
            required={(value, formvalues) => {
              const mainvalue = formvalues.newPassword
              return validateMatchingFields(value, mainvalue)
            }}
            className="mt36"
            name="newPasswordConfirm"
            disabled={isLoading}
            label="Confirmez votre nouveau mot de passe"
          />
          {formErrors && <FormError customMessage={formErrors} />}
        </div>
      </div>
    )
  }
}

PasswordForm.defaultProps = {
  formErrors: false,
}

PasswordForm.propTypes = {
  formErrors: PropTypes.oneOfType([
    PropTypes.array,
    PropTypes.bool,
    PropTypes.string,
  ]),
  isLoading: PropTypes.bool.isRequired,
}

PasswordForm.displayName = 'PasswordForm'

export default withProfileForm(
  PasswordForm,
  {
    routeMethod: 'POST',
    routePath: 'users/current/change-password',
  },
  initialValues,
  null
)
