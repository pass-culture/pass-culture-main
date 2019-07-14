import React, { Fragment } from 'react'

import { CheckBoxField, EmailField, InputField, PasswordField } from '../../forms/inputs'

const FormFields = () => (
  <Fragment>
    <InputField
      autoComplete="name"
      className="mb28"
      label="Identifiant"
      name="publicName"
      placeholder="Mon nom ou pseudo"
      required
      sublabel="...que verront les autres utilisateurs : "
    />
    <EmailField
      autoComplete="email"
      className="mb28"
      label="Adresse e-mail"
      name="email"
      placeholder="nom@exemple.fr"
      required
      sublabel="...pour se connecter et récupérer son mot de passe en cas d’oubli : "
    />
    <PasswordField
      autoComplete="new-password"
      className="mb28"
      label="Mot de passe"
      name="password"
      placeholder="Mon mot de passe"
      required
      sublabel="...pour se connecter : "
    />
    <CheckBoxField
      className="field-checkbox"
      name="contact_ok"
      required
    >
      <span className="pc-final-form-label">
        {'J’accepte d’être contacté par e-mail pour donner mon avis sur le '}
        <a
          href="http://passculture.beta.gouv.fr"
          rel="noopener noreferrer"
          target="_blank"
        >
          {'pass Culture'}
        </a>
        <span className="pc-final-form-asterisk">{'*'}</span>
      </span>
    </CheckBoxField>
  </Fragment>
)

export default FormFields
