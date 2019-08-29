import React from 'react'
import PropTypes from 'prop-types'

import { FormError, FormFooter } from '../../forms'
import { InputField } from '../../forms/inputs'
import withResetForm from './withResetForm'

const cancelOptions = {
  className: 'is-white-text',
  disabled: false,
  label: 'Annuler',
  url: '/connexion',
}

const submitOptions = {
  className: 'is-bold is-white-text',
  label: 'OK',
}

export const RawRequestEmailForm = ({ canSubmit, isLoading, formErrors }) => (
  <div
    className="is-full-layout flex-rows"
    id="reset-password-page-request"
  >
    <main
      className="pc-main is-white-text flex-1"
      role="main"
    >
      <div className="pc-scroll-container">
        <div className="is-full-layout flex-rows flex-center padded-2x">
          <h2 className="mb36">
            <span className="is-block is-italic is-medium fs22">
              {'Renseignez votre adresse e-mail pour réinitialiser votre mot de passe.'}
            </span>
            <span className="is-block is-regular fs13 mt18">
              <span>{'*'}</span>
              &nbsp;{'Champs obligatoires'}
            </span>
          </h2>
          <div>
            <InputField
              disabled={isLoading}
              label="Adresse e-mail"
              name="email"
              placeholder="Ex. : nom@domaine.fr"
              required
              theme="primary"
            />
            {formErrors && <FormError customMessage={formErrors} />}
          </div>
        </div>
      </div>
    </main>
    <FormFooter
      cancel={cancelOptions}
      submit={{ ...submitOptions, disabled: !canSubmit }}
    />
  </div>
)

RawRequestEmailForm.defaultProps = {
  formErrors: false,
}

RawRequestEmailForm.propTypes = {
  canSubmit: PropTypes.bool.isRequired,
  formErrors: PropTypes.oneOfType([PropTypes.array, PropTypes.bool, PropTypes.string]),
  isLoading: PropTypes.bool.isRequired,
}

export default withResetForm(RawRequestEmailForm, null, '/users/reset-password', 'POST')
