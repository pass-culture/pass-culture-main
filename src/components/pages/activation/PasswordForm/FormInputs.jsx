import React from 'react'
import PropTypes from 'prop-types'

import { FormError } from '../../../forms'
import { validateMatchingFields } from '../../../forms/validators'
import { CheckBoxField, HiddenField, PasswordField } from '../../../forms/inputs'

const Undefined = () => undefined

const isRequired = (value, formvalues) => {
  const mainvalue = formvalues.newPassword

  return validateMatchingFields(value, mainvalue)
}

const FormInputs = ({ formValues, formErrors, isLoading }) => {
  const { email } = formValues

  return (
    <div className="pc-scroll-container">
      <div className="is-full-layout flex-rows flex-center">
        <h2 className="fs22 is-italic is-medium">
          {'Pour commencer, choisissez votre mot de passe.'}
        </h2>
        <div className="fs13 mt12">{'* Champs obligatoires'}</div>
        <div className="mt36">
          <div className="fs19">{'Adresse e-mail :'}</div>
          <div
            className="is-bold fs20"
            id="activation-email"
          >
            {email}
          </div>
        </div>
        <PasswordField
          className="mt36"
          disabled={isLoading}
          help="Il doit contenir au minimum 12 caractères, une majuscule, une minuscule, un chiffre et un caractère spécial."
          id="activation-newPassword"
          label="Nouveau mot de passe"
          name="newPassword"
          required={Undefined}
          theme="primary"
        />
        <PasswordField
          className="mt36"
          disabled={isLoading}
          id="activation-newPasswordConfirm"
          label="Confirmez le mot de passe"
          name="newPasswordConfirm"
          required={isRequired}
          theme="primary"
        />
        <CheckBoxField
          className="field-checkbox"
          name="cguCheckBox"
        >
          <span>
            {'J’ai lu et accepte les '}
            <a
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
