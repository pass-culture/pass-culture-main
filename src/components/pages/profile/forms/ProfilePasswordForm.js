/* eslint
  react/jsx-one-expression-per-line: 0 */
import PropTypes from 'prop-types'
import React from 'react'

import { FormError } from '../../../forms'
import { isEmpty } from '../../../../utils/strings'
import { PasswordField } from '../../../forms/inputs'
import withProfileForm from './withProfileForm'
import validatePasswordForm from '../validators/validatePasswordForm'

// NOTE: les anciens mot de passe lors de la phase beta
// n'avaient de règle de validation
// FIXME: peu être mettre un if avec une version du package.json
// si on considére que la v1 correspond à la mise en ligne d'octobre
const ERROR_OLD_PASSWORD = "L'ancien mot de passe est manquant"

const initialValues = {
  newPassword: null,
  newPasswordConfirm: null,
  oldPassword: null,
}

// azertyazertyP1$
class ProfilePasswordForm extends React.PureComponent {
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
            required
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

ProfilePasswordForm.defaultProps = {
  formErrors: false,
}

ProfilePasswordForm.propTypes = {
  formErrors: PropTypes.oneOfType([
    PropTypes.array,
    PropTypes.bool,
    PropTypes.string,
  ]),
  isLoading: PropTypes.bool.isRequired,
}

ProfilePasswordForm.displayName = 'ProfilePasswordForm'

export default withProfileForm(
  ProfilePasswordForm,
  validatePasswordForm,
  // TODO -> plutot les options de route par un objet
  'users/current/change-password',
  'POST',
  false,
  initialValues
)
