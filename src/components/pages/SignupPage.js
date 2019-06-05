/* eslint
  react/jsx-one-expression-per-line: 0 */
import { Field, Form, SubmitButton } from 'pass-culture-shared'
import React from 'react'
import { Portal } from 'react-portal'
import { NavLink } from 'react-router-dom'

import { withRedirectToDiscoveryOrTypeformAfterLogin } from '../hocs'
import Main from '../layout/Main'

export class RawSignupPage extends React.PureComponent {
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
        <div className="section pc-final-form">
          <h2 className="mb36">
            <span className="is-block is-italic is-medium fs22">
              Une minute pour créer un compte, et puis c&apos;est tout&nbsp;!
            </span>
            <span className="is-block is-regular fs13 is-grey-text mt18">
              <span className="is-purple-text">*</span>
              &nbsp;Champs obligatoires
            </span>
          </h2>
          <Form
            name="user"
            action="/users/signup/webapp"
            layout="vertical"
            handleSuccessNotification={null}
            handleSuccessRedirect={() => '/decouverte'}
          >
            <div className="mt36">
              <Field
                autoComplete="name"
                label="Identifiant"
                name="publicName"
                placeholder="Mon nom ou pseudo"
                required
                sublabel="que verront les autres utilisateurs"
                type="text"
              />
            </div>
            <div className="mt36">
              <Field
                autoComplete="email"
                label="Adresse e-mail"
                name="email"
                placeholder="nom@exemple.fr"
                required
                sublabel="pour se connecter et récupérer son mot de passe en cas d'oubli"
                type="email"
              />
            </div>
            <div className="mt36">
              <Field
                autoComplete="new-password"
                label="Mot de passe"
                name="password"
                placeholder="Mon mot de passe"
                required
                sublabel="pour se connecter"
                type="password"
              />
            </div>
            <div className="mt36">
              <Field
                label={(
                  <span className="subtitle">
                    {' '}
                    {
                      "J'accepte d'être contacté par mail pour donner mon avis sur le"
                    }{' '}
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
            </div>

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

export default withRedirectToDiscoveryOrTypeformAfterLogin(RawSignupPage)
