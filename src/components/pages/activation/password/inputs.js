/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import PropTypes from 'prop-types'

import { FormError } from '../../../forms'
import { validateMatchingFields } from '../../../forms/validators'
import { HiddenField, PasswordField } from '../../../forms/inputs'

const FormInputs = ({ formValues, formErrors, isLoading }) => {
  const { email } = formValues
  return (
    <div className="pc-scroll-container">
      <div className="is-full-layout flex-rows flex-center">
        <div className="fs22">
          <h2 className="is-italic is-medium">
            <span className="is-block">
              Pour commencer, choisissez votre mot de passe.
            </span>
          </h2>
          <p className="is-block is-regular fs13 mt18">
            <span>*</span>
            &nbsp;Champs obligatoires
          </p>
        </div>
        <div>
          <div className="mt36">
            <span className="is-block is-normal fs19">Adresse e-mail</span>
            <span className="is-block is-bold fs20" id="activation-email">
              {email}
            </span>
          </div>
          <PasswordField
            required={() => undefined}
            theme="primary"
            className="mt36"
            name="newPassword"
            disabled={isLoading}
            id="activation-newPassword"
            label="Nouveau mot de passe"
            help="Il doit contenir au minimum 12 caractères, une majuscule, une minuscule, un chiffre et un caractère spécial."
          />
          <PasswordField
            required={(value, formvalues) => {
              const mainvalue = formvalues.newPassword
              return validateMatchingFields(value, mainvalue)
            }}
            theme="primary"
            className="mt36"
            disabled={isLoading}
            name="newPasswordConfirm"
            id="activation-newPasswordConfirm"
            label="Confirmez le mot de passe"
          />
          <HiddenField name="email" id="activation-email-hidden" />
          <HiddenField name="token" id="activation-token-hidden" />
          {/* gestion des retours erreurs de l'API */}
          <HiddenField name="global" id="activation-global-hidden" />
          <HiddenField name="identifier" id="activation-identifier-hidden" />
          {formErrors && <FormError customMessage={formErrors} />}
        </div>
      </div>
    </div>
  )
}

FormInputs.defaultProps = {
  formErrors: false,
}

FormInputs.propTypes = {
  formErrors: PropTypes.oneOfType([
    PropTypes.array,
    PropTypes.bool,
    PropTypes.string,
  ]),
  formValues: PropTypes.object.isRequired,
  isLoading: PropTypes.bool.isRequired,
}

export default FormInputs
