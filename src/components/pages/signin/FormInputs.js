import React from 'react'
import { Link } from 'react-router-dom'
import { validateRequiredField } from '../../forms/validators'
import { EmailField, PasswordField } from '../../forms/inputs'

const FormInputs = () => (
  <div>
    <input
      name="name"
      type="hidden"
      value="user"
    />
    <EmailField
      className="mb36"
      id="user-identifier"
      label="Adresse e-mail"
      name="identifier"
      placeholder="Identifiant (e-mail)"
      required
    />
    <PasswordField
      // NOTE on ne teste pas la force du password au signin
      className="mb36"
      id="user-password"
      label="Mot de passe"
      name="password"
      placeholder="Mot de passe"
      required={validateRequiredField}
    />
    <Link
      className="is-white-text is-underline fs16"
      to="/mot-de-passe-perdu"
    >
      <span>{'Mot de passe oublié ?'}</span>
    </Link>
  </div>
)

export default FormInputs
