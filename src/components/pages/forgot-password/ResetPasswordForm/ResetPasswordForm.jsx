import PropTypes from 'prop-types'
import React, { Fragment } from 'react'

import FormError from '../../../forms/FormError'
import FormFooter from '../../../forms/FormFooter'
import HiddenField from '../../../forms/inputs/HiddenField'
import PasswordField from '../../../forms/inputs/PasswordField'
import withNotRequiredLogin from '../../../hocs/with-login/withNotRequiredLogin'
import withResetForm from '../hocs/withResetForm'

const cancelOptions = {
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

export const ResetPasswordForm = ({ canSubmit, formErrors, isLoading }) => (
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
          disabled={isLoading}
          label="Saisis ton nouveau mot de passe"
          name="newPassword"
          required
          theme="primary"
        />
        <PasswordField
          disabled={isLoading}
          label="Confirmes ton nouveau mot de passe"
          name="newPasswordConfirm"
          required
          theme="primary"
        />
        <HiddenField name="token" />
        {formErrors && <FormError customMessage={formErrors} />}
      </div>
    </div>
    <FormFooter
      cancel={cancelOptions}
      submit={[{ ...submitOptions, disabled: !canSubmit }]}
    />
  </Fragment>
)

ResetPasswordForm.defaultProps = {
  formErrors: false,
}

ResetPasswordForm.propTypes = {
  canSubmit: PropTypes.bool.isRequired,
  formErrors: PropTypes.oneOfType([PropTypes.array, PropTypes.bool, PropTypes.string]),
  isLoading: PropTypes.bool.isRequired,
}

export default withNotRequiredLogin(
  withResetForm(ResetPasswordForm, null, '/users/new-password', 'POST')
)
