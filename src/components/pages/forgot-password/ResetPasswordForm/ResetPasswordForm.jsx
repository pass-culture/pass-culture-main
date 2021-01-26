import { FORM_ERROR } from 'final-form'
import React, { Fragment } from 'react'

import FormError from '../../../forms/FormError'
import FormFooter from '../../../forms/FormFooter'
import HiddenField from '../../../forms/inputs/HiddenField'
import PasswordField from '../../../forms/inputs/PasswordField'
import withNotRequiredLogin from '../../../hocs/with-login/withNotRequiredLogin'
import withResetForm, { resetFormWrappedComponentPropTypes } from '../hocs/withResetForm'

const cancelLink = {
  className: 'is-white-text',
  disabled: false,
  label: 'Annuler',
  url: '/connexion',
}

const submitOptions = {
  className: 'is-bold is-white-text',
  id: 'reset-password-submit',
  label: 'OK',
}

export const ResetPasswordForm = props => {
  return (
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
          <p className="mt12 fs16">
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
            disabled={props.isLoading}
            label="Saisis ton nouveau mot de passe"
            name="newPassword"
            required
            theme="primary"
          />
          <PasswordField
            disabled={props.isLoading}
            label="Confirmes ton nouveau mot de passe"
            name="newPasswordConfirm"
            required
            theme="primary"
          />
          <HiddenField name="token" />
          {props.hasValidationErrors && props.validationErrors[FORM_ERROR] && (
            <FormError customMessage={props.validationErrors[FORM_ERROR]} />
          )}
        </div>
      </div>
      <FormFooter items={[cancelLink, { ...submitOptions, disabled: !props.canSubmit }]} />
    </Fragment>
  )
}

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
