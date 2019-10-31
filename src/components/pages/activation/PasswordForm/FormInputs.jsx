import React from 'react'
import PropTypes from 'prop-types'

import FormError from '../../../forms/FormError'
import validateMatchingFields from '../../../forms/validators/validateMatchingFields'
import CheckBoxField from '../../../forms/inputs/CheckBoxField'
import HiddenField from '../../../forms/inputs/HiddenField'
import PasswordField from '../../../forms/inputs/PasswordField'

const Undefined = () => undefined

const isRequired = (value, formValues) => validateMatchingFields(value, formValues.newPassword)

const FormInputs = ({ formValues, formErrors, isLoading }) => {
  const { email } = formValues

  return (
    <div>
      <div className="logout-form-header">
        <div className="logout-form-title">
          {'Pour commencer, choisissez votre mot de passe.'}
        </div>
        <div className="logout-form-mandatory-label">
          {'* Champs obligatoires'}
        </div>
      </div>
      <div className="logout-form-header">
        <div className="activation-email-label">
          {'Adresse e-mail :'}
        </div>
        <div className="activation-email">
          {email}
        </div>
      </div>
      <PasswordField
        disabled={isLoading}
        id="activation-newPassword"
        label="Nouveau mot de passe"
        name="newPassword"
        required={Undefined}
        sublabel="Il doit contenir au minimum 12 caractères, une majuscule, une minuscule, un chiffre et un caractère spécial."
        theme="primary"
      />
      <PasswordField
        disabled={isLoading}
        id="activation-newPasswordConfirm"
        label="Confirmez le mot de passe"
        name="newPasswordConfirm"
        required={isRequired}
        theme="primary"
      />
      <CheckBoxField name="cguCheckBox">
        <span>
          {'J’ai lu et accepte les '}
          <a
            className="logout-form-link"
            href="https://pass.culture.fr/assets/docs/cgu-j.html"
            id="accept-cgu-link"
            rel="noopener noreferrer"
            target="_blank"
          >
            {'Conditions générales d’utilisation'}
          </a>
          {' du pass Culture. *'}
        </span>
      </CheckBoxField>
      <HiddenField
        id="activation-email-hidden"
        name="email"
      />
      <HiddenField
        id="activation-token-hidden"
        name="token"
      />
      <HiddenField
        id="activation-global-hidden"
        name="global"
      />
      <HiddenField
        id="activation-identifier-hidden"
        name="identifier"
      />
      {formErrors && <FormError customMessage={formErrors} />}
    </div>
  )
}

FormInputs.defaultProps = {
  formErrors: false,
}

FormInputs.propTypes = {
  formErrors: PropTypes.oneOfType([PropTypes.array, PropTypes.bool, PropTypes.string]),
  formValues: PropTypes.shape().isRequired,
  isLoading: PropTypes.bool.isRequired,
}

export default FormInputs
