import get from 'lodash.get'
import React from 'react'
import { NavLink } from 'react-router-dom'

import PageWrapper from '../layout/PageWrapper'
import FormField from '../layout/FormField'
import SubmitButton from '../layout/SubmitButton'
import withSign from '../hocs/withSign'
import { NEW } from '../../utils/config'

const inputClassName = 'input block col-12 mb2 red'

const Label = ({ title }) => {
  return <div className="mb1">{title}</div>
}

const SigninPage = ({ errors }) => {
  return (
    <PageWrapper name="sign-in" Tag="form" redBg>
      <div className="form-container">
        <div className='section'>
          <h1 className='title is-1 is-italic'>Bonjour&nbsp;!</h1>
          <h2 className='subtitle is-2 is-italic'>
            Identifiez-vous <br />
            pour accéder aux offres.
          </h2>
        </div>
        <FormField
          className={inputClassName}
          type="email"
          collectionName="users"
          label={<Label title="Adresse e-mail:" />}
          name="identifier"
          placeholder="Identifiant (email)"
          autoComplete="email"
        />
        <FormField
          className={inputClassName}
          collectionName="users"
          label={<Label title="Mot de passe" />}
          name="password"
          type="password"
          placeholder="Mot de passe"
          autoComplete="current-password"
        />
        <div className="sign__error mt1">{errors}</div>
      </div>
      <footer>
        <SubmitButton
          getBody={form => form.usersById[NEW]}
          getIsDisabled={form =>
            !get(form, 'usersById._new_.identifier') ||
            !get(form, 'usersById._new_.password')
          }
          className="button is-primary is-inverted"
          path="users/signin"
          storeKey="users"
          text="Connexion"
        />
        <NavLink to="/inscription" className='button is-secondary'>
          Inscription
        </NavLink>
      </footer>
    </PageWrapper>
  )
}

export default withSign(SigninPage)
