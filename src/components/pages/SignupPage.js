import { Field, Form, SubmitButton } from 'pass-culture-shared'
import React from 'react'
import { Portal } from 'react-portal'
import { NavLink } from 'react-router-dom'

import Main from '../layout/Main'

class SignupPage extends React.PureComponent {
  constructor() {
    super()
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
      <Main name="sign-up" footer={this.renderPageFooter}>
        <div className="section">
          <h2 className="subtitle is-italic">
            {"Une minute pour créer un compte, et puis c'est tout !"}
          </h2>

          <br />
          <Form
            name="user"
            action="/users/signup"
            layout="vertical"
            handleSuccessNotification={null}
            handleSuccessRedirect={() => '/decouverte'}
          >
            <Field
              autoComplete="name"
              label="Identifiant"
              name="publicName"
              placeholder="Mon nom ou pseudo"
              required
              sublabel="que verront les autres utilisateurs"
              type="text"
            />
            <Field
              autoComplete="email"
              label="Adresse e-mail"
              name="email"
              placeholder="nom@exemple.fr"
              required
              sublabel="pour se connecter et récupérer son mot de passe en cas d'oubli"
              type="email"
            />
            <Field
              autoComplete="new-password"
              label="Mot de passe"
              name="password"
              placeholder="Mon mot de passe"
              required
              sublabel="pour se connecter"
              type="password"
            />
            <br />
            <Field
              label={(
                <span className="subtitle">
                  {' '}
                  {
                    "J'accepte d'être contacté par mail pour donner mon avis sur le"
                  }
                  {' '}
                  <a
                    href="http://passculture.beta.gouv.fr"
                    style={{ textDecoration: 'underline' }}
                  >
                    Pass Culture
                  </a>
                  .
                </span>
)}
              name="contact_ok"
              required
              type="checkbox"
            />

            <Portal node={$footer}>
              <SubmitButton className="button is-primary is-inverted">
                Créer
              </SubmitButton>
              <NavLink to="/connexion" className="button is-secondary">
                {"J'ai déjà un compte"}
              </NavLink>
            </Portal>
          </Form>
        </div>
      </Main>
    )
  }
}

export default SignupPage
