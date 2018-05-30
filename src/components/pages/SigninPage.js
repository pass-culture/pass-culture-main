import get from 'lodash.get'
import React from 'react'
import { NavLink } from 'react-router-dom'

import PageWrapper from '../layout/PageWrapper'
import FormField from '../layout/FormField'
import Logo from '../layout/Logo'
import SubmitButton from '../layout/SubmitButton'
import withSign from '../hocs/withSign'
import { NEW } from '../../utils/config'

const Label = ({ title }) => {
  return <div className="mb1">{title}</div>
}

const SigninPage = ({ errors }) => {
  return (
    <PageWrapper name="sign-in" noHeader noContainer>
      <div className='columns'>
        <div className='column is-half logo-column'>
          <Logo />
        </div>
        <div className='column is-one-third'>
          <section className='hero has-text-grey'>
            <div className='hero-body'>
              <h1 className='title is-spaced is-1'>
                <span className="has-text-weight-bold ">Bienvenue</span>
                <span className="has-text-weight-semibold">dans la version bêta</span>
                <span className="has-text-weight-normal">du Pass Culture pro.</span>
              </h1>
              <p className='subtitle'>Et merci de votre participation pour nous aider à l'améliorer !</p>
              <form>
                <FormField
                  className='input is-rounded'
                  type="email"
                  collectionName="users"
                  label={<Label title="Adresse e-mail:" />}
                  name="identifier"
                  placeholder="Identifiant (email)"
                  autoComplete="email"
                />
                <FormField
                  className='input is-rounded'
                  collectionName="users"
                  label={<Label title="Mot de passe" />}
                  name="password"
                  type="password"
                  placeholder="Mot de passe"
                  autoComplete="current-password"
                />
                <div className="errors">{errors}</div>
                <div className='field buttons-field'>
                  <NavLink to="/inscription" className="button is-secondary">
                    Créer un compte
                  </NavLink>
                  <SubmitButton
                    text="Se connecter"
                    className="button is-primary is-outlined"
                    getBody={form => form.usersById[NEW]}
                    getIsDisabled={form =>
                      !get(form, 'usersById._new_.publicName') ||
                      !get(form, 'usersById._new_.email') ||
                      !get(form, 'usersById._new_.password')
                    }
                    path="users"
                    storeKey="users"
                  />
                </div>
              </form>
            </div>
          </section>
        </div>
      </div>
    </PageWrapper>
  )
}

export default withSign(SigninPage)
