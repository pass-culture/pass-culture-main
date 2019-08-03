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
        <div className="fs22">
          <h2 className="is-italic is-medium">
            <span className="is-block">{'Pour commencer, choisissez votre mot de passe.'}</span>
          </h2>
          <p className="is-block is-regular fs13 mt12">
            <span>{'*'}</span>
            &nbsp;{'Champs obligatoires'}
          </p>
        </div>
        <div>
          <div className="mt36">
            <span className="is-block is-normal fs19">{'Adresse e-mail'}</span>
            <span
              className="is-block is-bold fs20"
              id="activation-email"
            >
              {email}
            </span>
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
            className="checkbox-accept-CGU"
            name="cguCheckBox"
            required
          >
            <span className="pc-final-form-label">
              {'J’ai lu et accepte les '}
              <a
                className="fs16"
                href="https://pass.culture.fr/assets/docs/cgu-j.html"
                id="accept-cgu-link"
                rel="noopener noreferrer"
                target="_blank"
              >
                {'Conditions générales d’utilisation'}
              </a>
              {' du pass Culture'}
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
