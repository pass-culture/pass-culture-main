import React, { Fragment } from 'react'

import FormError from '../../../forms/FormError'
import FormFooter from '../../../forms/FormFooter'
import InputField from '../../../forms/inputs/InputField'
import withNotRequiredLogin from '../../../hocs/with-login/withNotRequiredLogin'
import withResetForm, {
  resetFormWrappedComponentDefaultPropTypes,
  resetFormWrappedComponentPropTypes,
} from '../hocs/withResetForm'

export const RequestEmailForm = ({ canSubmit, hasSubmitErrors, isLoading }) => (
  <Fragment>
    <div>
      <div className="logout-form-header">
        <div className="logout-form-title">
          {'Renseigne ton adresse e-mail pour réinitialiser ton mot de passe.'}
        </div>
      </div>
      <div>
        <InputField
          ariaLabel="Adresse e-mail (Exemple : nom@domaine.fr)"
          disabled={isLoading}
          label="Adresse e-mail"
          name="email"
          placeholder="Exemple : nom@domaine.fr"
          theme="white"
        />
        {hasSubmitErrors && (
          <FormError customMessage="Un problème est survenu pendant la réinitialisation du mot de passe, réessaie plus tard." />
        )}
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

RequestEmailForm.defaultPropTypes = resetFormWrappedComponentDefaultPropTypes
RequestEmailForm.propTypes = resetFormWrappedComponentPropTypes

export default withNotRequiredLogin(
  withResetForm(RequestEmailForm, null, '/users/reset-password', 'POST')
)
