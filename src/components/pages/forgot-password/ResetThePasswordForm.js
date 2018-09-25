/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import PropTypes from 'prop-types'

import { FormError } from '../../forms'
import { HiddenField, PasswordField } from '../../forms/inputs'
import FormFooter from './FormFooter'
import withResetForm from './withResetForm'

class ResetThePasswordForm extends React.PureComponent {
  render() {
    const { canSubmit, formErrors, isLoading } = this.props
    return (
      <div
        id="reset-password-page-request"
        className="is-full-layout flex-rows"
      >
        <main role="main" className="pc-main is-white-text flex-1">
          <div className="pc-scroll-container">
            <div className="is-full-layout flex-rows flex-center padded-2x">
              <div className="fs22">
                <h2 className="is-italic is-medium">
                  <span className="is-block">Saisissez ci-dessous</span>
                  <span className="is-block">votre nouveau mot de passe.</span>
                </h2>
                <p className="mt12 fs16">
                  Il doit contenir au minimum 12 caractères, une majuscule, une
                  minuscule, un chiffre et un caractère spécial.
                </p>
                <p className="is-block is-regular fs13 mt18">
                  <span>*</span>
                  &nbsp;Champs obligatoires
                </p>
              </div>
              <div>
                <PasswordField
                  required
                  theme="primary"
                  className="mt36"
                  name="newPassword"
                  disabled={isLoading}
                  label="Saisissez votre nouveau mot de passe"
                />
                <PasswordField
                  required
                  theme="primary"
                  className="mt36"
                  name="newPasswordConfirm"
                  disabled={isLoading}
                  label="Confirmez votre nouveau mot de passe"
                />
                <HiddenField name="token" />
                {formErrors && <FormError customMessage={formErrors} />}
              </div>
            </div>
          </div>
        </main>
        <FormFooter
          cancel={{
            className: 'is-white-text',
            disabled: false,
            label: 'Annuler',
            url: '/connexion',
          }}
          submit={{
            className: 'is-bold is-white-text',
            disabled: !canSubmit,
            label: 'OK',
          }}
        />
      </div>
    )
  }
}

ResetThePasswordForm.defaultProps = {
  formErrors: false,
}

ResetThePasswordForm.propTypes = {
  canSubmit: PropTypes.bool.isRequired,
  formErrors: PropTypes.oneOfType([
    PropTypes.array,
    PropTypes.bool,
    PropTypes.string,
  ]),
  isLoading: PropTypes.bool.isRequired,
}

export default withResetForm(
  ResetThePasswordForm,
  null,
  '/users/new-password',
  'POST'
)
