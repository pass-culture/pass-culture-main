import {
  Field,
  Form,
  SubmitButton
} from 'pass-culture-shared'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'

import Logo from '../layout/Logo'
import PageWrapper from '../layout/PageWrapper'


class SigninPage extends Component {

  componentDidUpdate () {
    const { history, user } = this.props
    if (user) {
      history.push('/offres')
    }
  }

  render () {
    const { errors } = this.props
    return (
      <PageWrapper name="sign-in" fullscreen>
        <div className='logo-side'>
          <Logo noLink />
        </div>
        <div className='container'>
          <div className='columns'>
            <div className='column is-offset-6 is-two-fifths'>
              <section className='hero has-text-grey'>
                <div className='hero-body'>
                  <h1 className='title is-spaced is-1'>
                    <span className="has-text-weight-bold ">
                      Bienvenue
                    </span>{' '}
                    <span className="has-text-weight-semibold">
                      dans la version bêta
                    </span>
                    <span className="has-text-weight-normal">
                      du Pass Culture pro.
                    </span>
                  </h1>
                  <h2 className='subtitle is-2'>
                    Et merci de votre participation pour nous aider à l'améliorer !
                  </h2>
                  <Form
                    action='/users/signin'
                    layout='vertical'
                    name='user'
                    successNotification={null} >
                    <Field
                      label='Adresse e-mail'
                      name='identifier'
                      placeholder="Identifiant (email)"
                      required
                      type='email' />
                    <Field
                      autoComplete="current-password"
                      label='Mot de passe'
                      name='password'
                      placeholder='Mot de passe'
                      required
                      type='password' />
                    <div className="errors">{errors}</div>
                    <div className='field buttons-field'>
                      <NavLink to="/inscription" className="button is-secondary">
                        Créer un compte
                      </NavLink>
                      <SubmitButton className="button is-primary is-outlined">
                        Se connecter
                      </SubmitButton>
                    </div>
                  </Form>
                </div>
              </section>
            </div>
          </div>
        </div>
      </PageWrapper>
    )
  }
}

export default compose(
  withRouter,
  connect(
    state => ({
      user: state.user,
    })
  )
)(SigninPage)
