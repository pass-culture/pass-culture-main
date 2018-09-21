/* eslint
  react/jsx-one-expression-per-line: 0 */
import { Field, Form, SubmitButton } from 'pass-culture-shared'
import React from 'react'
import { Portal } from 'react-portal'
import { NavLink } from 'react-router-dom'

import Main from '../layout/Main'

const inputClassName = 'pc-form-text-input input block col-12 mb2 red'

class SigninPage extends React.PureComponent {
  constructor() {
    super()
    this.$footer = null
    this.state = { $footer: null }
  }

  componentDidMount() {
    this.setState({ $footer: this.$footer })
  }

  // FIXME -> [PERFS] remove ReactPortal
  renderPageFooter = () => (
    <footer
      ref={elt => {
        this.$footer = elt
      }}
    />
  )

  render() {
    const { $footer } = this.state
    return (
      <Main name="sign-in" redBg footer={this.renderPageFooter}>
        <div className="section form-container pc-final-form is-clipped">
          <h1 className="text-left fs32">
            <span className="is-bold is-italic is-block">Bonjour&nbsp;!</span>
          </h1>
          <p className="text-left is-italic is-medium fs22">
            <span className="is-block">Identifiez-vous</span>
            <span className="is-block">pour accéder aux offres.</span>
          </p>
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
              required
            />
            <Field
              autoComplete="current-password"
              className={inputClassName}
              label="Mot de passe:"
              name="password"
              placeholder="Mot de passe"
              type="password"
              required
            />
            <p>
              <NavLink to="/mot-de-passe-perdu">
                <span>Mot de passe oublié&nbsp;?</span>
              </NavLink>
            </p>

            <Portal node={$footer}>
              <SubmitButton className="button is-primary is-inverted">
                Connexion
              </SubmitButton>
              <NavLink to="/inscription" className="button is-secondary">
                Inscription
              </NavLink>
            </Portal>
          </Form>
        </div>
      </Main>
    )
  }
}

export default SigninPage
