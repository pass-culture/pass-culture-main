import { FORM_ERROR } from 'final-form'
import React, { Fragment } from 'react'

import FormError from '../../../forms/FormError'
import FormFooter from '../../../forms/FormFooter'
import HiddenField from '../../../forms/inputs/HiddenField'
import PasswordField from '../../../forms/inputs/PasswordField'
import withNotRequiredLogin from '../../../hocs/with-login/withNotRequiredLogin'
import withResetForm, {
  resetFormWrappedComponentDefaultPropTypes,
  resetFormWrappedComponentPropTypes,
} from '../hocs/withResetForm'

const cancelLink = {
  className: 'is-white-text',
  disabled: false,
  label: 'Annuler',
  url: '/connexion',
  id: 'cancel-link',
}

const submitOptions = {
  className: 'is-bold is-white-text',
  id: 'reset-password-submit',
  label: 'OK',
}

export const ResetPasswordForm = ({
  isLoading,
  hasValidationErrors,
  validationErrors,
  canSubmit,
}) => (
  <Fragment>
    <div>
      <div className="fs22">
        <h2 className="is-italic is-medium">
          <span className="is-block">
            {'Saisis ci-dessous'}
          </span>
          <span className="is-block">
            {'ton nouveau mot de passe.'}
          </span>
        </h2>
        <p
          className="mt12 fs16"
          id="password-rules"
        >
          {
            'Il doit contenir au minimum 12 caractères, une majuscule, une minuscule, un chiffre et un caractère spécial.'
          }
        </p>
        <p className="is-block is-regular fs13 mt18">
          <span>
            {'*'}
          </span>
          &nbsp;
          {'Champs obligatoires'}
        </p>
      </div>
      <div>
        <PasswordField
          describedBy="password-rules"
          disabled={isLoading}
          label="Saisis ton nouveau mot de passe"
          name="newPassword"
          required
          theme="primary"
        />
        <PasswordField
          describedBy="password-rules"
          disabled={isLoading}
          label="Confirmes ton nouveau mot de passe"
          name="newPasswordConfirm"
          required
          theme="primary"
        />
        <HiddenField name="token" />
        {hasValidationErrors && validationErrors[FORM_ERROR] && (
          <FormError customMessage={validationErrors[FORM_ERROR]} />
        )}
      </div>
    </div>
    <FormFooter items={[cancelLink, { ...submitOptions, disabled: !canSubmit }]} />
  </Fragment>
)

ResetPasswordForm.defaultPropTypes = resetFormWrappedComponentDefaultPropTypes
ResetPasswordForm.propTypes = resetFormWrappedComponentPropTypes

function validator(formValues) {
  const validationErrors = {}
  if (formValues.newPasswordConfirm && formValues.newPassword !== formValues.newPasswordConfirm) {
    validationErrors[FORM_ERROR] = 'Les mots de passe ne sont pas les mêmes.'
  }
  return validationErrors
}

export default withNotRequiredLogin(
  withResetForm(ResetPasswordForm, validator, '/users/new-password', 'POST')
)
