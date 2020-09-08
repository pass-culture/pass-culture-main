import PropTypes from 'prop-types'
import React, { Fragment } from 'react'

import FormError from '../../../forms/FormError'
import FormFooter from '../../../forms/FormFooter'
import InputField from '../../../forms/inputs/InputField'
import withNotRequiredLogin from '../../../hocs/with-login/withNotRequiredLogin'
import withResetForm from '../hocs/withResetForm'

export const RequestEmailForm = ({ canSubmit, isLoading, formErrors }) => (
  <Fragment>
    <div>
      <div className="logout-form-header">
        <div className="logout-form-title">
          {'Renseigne ton adresse e-mail pour réinitialiser ton mot de passe.'}
        </div>
      </div>
      <div>
        <InputField
          disabled={isLoading}
          label="Adresse e-mail"
          name="email"
          placeholder="Ex. : nom@domaine.fr"
          theme="white"
        />
        {formErrors && <FormError customMessage={formErrors} />}
      </div>
    </div>
    <FormFooter
      items={[
        {
          className: 'is-white-text',
          id: 'np-cancel-link',
          label: 'Annuler',
          url: '/connexion',
        },
        {
          className: 'is-bold is-white-text',
          id: 'np-ok-button',
          label: 'OK',
          disabled: !canSubmit,
        },
      ]}
    />
  </Fragment>
)

RequestEmailForm.defaultProps = {
  formErrors: false,
}

RequestEmailForm.propTypes = {
  canSubmit: PropTypes.bool.isRequired,
  formErrors: PropTypes.oneOfType([PropTypes.array, PropTypes.bool, PropTypes.string]),
  isLoading: PropTypes.bool.isRequired,
}

export default withNotRequiredLogin(
  withResetForm(RequestEmailForm, null, '/users/reset-password', 'POST')
)
