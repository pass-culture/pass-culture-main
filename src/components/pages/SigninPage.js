import { Field, Form, SubmitButton } from 'pass-culture-shared'
import React, { Component } from 'react'
import { Portal } from 'react-portal'
import { NavLink } from 'react-router-dom'

import Main from '../layout/Main'

const inputClassName = 'input block col-12 mb2 red'

class SigninPage extends Component {
  constructor() {
    super()
    this.state = { $footer: null }
  }

  componentDidMount() {
    this.setState({ $footer: this.$footer })
  }

  render() {
    return (
      <Main name="sign-in" redBg>
        <div className="section form-container">
          <h1 className="title is-1 is-italic">
Bonjour&nbsp;!
          </h1>
          <h2 className="subtitle is-2 is-italic">
            Identifiez-vous 
            {' '}
            <br />
            pour accéder aux offres.
          </h2>

          <br />
          <Form
            action="/users/signin"
            layout="vertical"
            name="user"
            handleSuccessNotification={null}
            handleSuccessRedirect={() => '/decouverte'}
          >
            <Field
              autoComplete="email"
              className={inputClassName}
              label="Adresse e-mail:"
              name="identifier"
              placeholder="Identifiant (email)"
              type="email"
            />
            <Field
              autoComplete="current-password"
              className={inputClassName}
              label="Mot de passe:"
              name="password"
              placeholder="Mot de passe"
              type="password"
            />

            <Portal node={this.state.$footer}>
              <SubmitButton className="button is-primary is-inverted">
                Connexion
              </SubmitButton>
              <NavLink to="/inscription" className="button is-secondary">
                Inscription
              </NavLink>
            </Portal>
          </Form>
        </div>

        <footer ref={_e => (this.$footer = _e)} />
      </Main>
    )
  }
}

export default SigninPage
