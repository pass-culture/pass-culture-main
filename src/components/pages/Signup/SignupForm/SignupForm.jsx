import PropTypes from 'prop-types'
import React, { Fragment, PureComponent } from 'react'
import createDecorator from 'final-form-calculate'
import { NavLink } from 'react-router-dom'
import { Field, Form } from 'react-final-form'
import { CGU_URL } from '../../../../utils/config'
import Siren from '../../Offerer/OffererCreation/Fields/Siren/Siren'
import bindAddressAndDesignationFromSiren from '../../Offerer/OffererCreation/decorators/bindSirenFieldToDesignation'
import Icon from '../../../layout/Icon'
import PasswordField from '../../../layout/form/fields/PasswordField'

const addressAndDesignationFromSirenDecorator = createDecorator({
  field: 'siren',
  updates: bindAddressAndDesignationFromSiren,
})

const required = value => (value ? undefined : 'Required')

class SignupForm extends PureComponent {
  componentDidMount() {
    const script = document.createElement('script')

    script.src = '//js.hs-scripts.com/5119289.js'
    script.async = true
    script.type = 'text/javascript'
    script.id = 'hs-script-loader'
    script.defer = true

    document.body.appendChild(script)
  }

  componentWillUnmount() {
    const { closeNotification } = this.props
    closeNotification()
    const script = document.getElementById('hs-script-loader')
    document.body.removeChild(script)
  }

  renderCguContent = () => (
    <Fragment>
      {'J’ai lu et j’accepte les '}
      <a
        href={CGU_URL}
        id="accept-cgu-link"
        rel="noopener noreferrer"
        target="_blank"
      >
        {'Conditions Générales d’Utilisation'}
      </a>
    </Fragment>
  )

  onHandleSuccess = () => {
    const { redirectToConfirmation } = this.props

    redirectToConfirmation()
  }

  onHandleFail = () => {
    const { showNotification } = this.props

    showNotification('Formulaire non validé.', 'danger')
  }

  handleSubmit = values => {
    const { createNewProUser } = this.props

    createNewProUser(values, this.onHandleFail, this.onHandleSuccess)
  }

  render() {
    const { errors } = this.props

    return (
      <section>
        <div className="sign-up-wrapper">
          <h1 className="sign-up-title">
            {'Créez votre compte'}
          </h1>
          <h2 className="sign-up-sub-title">
            {'Nous vous invitons à prendre connaissance des '}
            <a
              className="sign-up-requirements"
              href="https://pass.culture.fr/ressources"
              rel="noopener noreferrer"
              target="_blank"
            >
              {'modalités de fonctionnement en cliquant ici '}
            </a>
            {'avant de renseigner les champs suivants.'}
          </h2>
          <div className="sign-up-tips">
            <span className="field-asterisk">
              {' *'}
            </span>
            {' Champs obligatoires'}
          </div>
          <div>
            {}
          </div>
          <Form
            decorators={[addressAndDesignationFromSirenDecorator]}
            onSubmit={this.handleSubmit}
          >
            {({ handleSubmit, valid }) => (
              <form onSubmit={handleSubmit}>
                <label>
                  {'Adresse e-mail'}
                  <span className="field-asterisk">
                    {' *'}
                  </span>
                  <p className="sub-label">
                    {'...pour se connecter et récupérer son mot de passe en cas d’oubli'}
                  </p>
                  <Field
                    component="input"
                    name="email"
                    placeholder="nom@exemple.fr"
                    type="text"
                    validate={required}
                  />
                  {errors && errors.email && (
                    <p className="errors">
                      <Icon
                        alt="Une erreur est survenue"
                        svg="picto-warning"
                      />
                      {errors && errors.email}
                    </p>
                  )}
                </label>

                <label>
                  {'Mot de passe'}
                  <span className="field-asterisk">
                    {' *'}
                  </span>
                  <p className="sub-label">
                    {'...pour se connecter'}
                  </p>
                  <PasswordField
                    name="password"
                    placeholder="Mon mot de passe"
                    validate={required}
                  />
                  {errors && errors.password && (
                    <p className="errors">
                      <Icon
                        alt="Une erreur est survenue"
                        svg="picto-warning"
                      />
                      {errors && errors.password}
                    </p>
                  )}
                </label>

                <label>
                  {'Nom'}
                  <span className="field-asterisk">
                    {' *'}
                  </span>
                  <Field
                    component="input"
                    name="lastName"
                    placeholder="Mon nom"
                    validate={required}
                  />
                  {errors && errors.lastName && (
                    <p className="errors">
                      <Icon
                        alt="Une erreur est survenue"
                        svg="picto-warning"
                      />
                      {errors && errors.lastName}
                    </p>
                  )}
                </label>

                <label>
                  {'Prénom'}
                  <span className="field-asterisk">
                    {' *'}
                  </span>
                  <Field
                    component="input"
                    name="firstName"
                    placeholder="Mon prénom"
                    validate={required}
                  />
                  {errors && errors.firstName && (
                    <p className="errors">
                      <Icon
                        alt="Une erreur est survenue"
                        svg="picto-warning"
                      />
                      {errors && errors.firstName}
                    </p>
                  )}
                </label>

                <label>
                  {'Téléphone'}
                  <span className="field-asterisk">
                    {' *'}
                  </span>
                  <p className="sub-label">
                    {'...utilisé uniquement par l’équipe du pass Culture'}
                  </p>
                  <Field
                    component="input"
                    name="phoneNumber"
                    placeholder="Mon numéro de téléphone"
                    validate={required}
                  />
                  {errors && errors.phoneNumber && (
                    <p className="errors">
                      <Icon
                        alt="Une erreur est survenue"
                        svg="picto-warning"
                      />
                      {errors && errors.phoneNumber}
                    </p>
                  )}
                </label>

                <Siren />

                <label className="sign-up-checkbox">
                  <Field
                    component="input"
                    name="newsletter_ok"
                    type="checkbox"
                  />
                  {'Je souhaite recevoir les actualités du pass Culture'}
                  {errors && errors.newsletter_ok && (
                    <p className="errors">
                      <Icon
                        alt="Une erreur est survenue"
                        svg="picto-warning"
                      />
                      {errors && errors.newsletter_ok}
                    </p>
                  )}
                </label>

                <label className="sign-up-checkbox">
                  <Field
                    component="input"
                    name="contact_ok"
                    type="checkbox"
                    validate={required}
                  />
                  {'J’accepte d’être contacté par e-mail pour donner mon avis sur le pass Culture'}
                  <span className="field-asterisk">
                    {' *'}
                  </span>
                  {errors && errors.contact_ok && (
                    <p className="errors">
                      <Icon
                        alt="Une erreur est survenue"
                        svg="picto-warning"
                      />
                      {errors && errors.contact_ok}
                    </p>
                  )}
                </label>

                <label className="sign-up-cgu">
                  <Field
                    component="input"
                    name="cgu_ok"
                    type="checkbox"
                    validate={required}
                  />
                  {this.renderCguContent()}
                  <span className="field-asterisk">
                    {' *'}
                  </span>
                  {errors && errors.cgu_ok && (
                    <p className="errors">
                      <Icon
                        alt="Une erreur est survenue"
                        svg="picto-warning"
                      />
                      {errors && errors.cgu_ok}
                    </p>
                  )}
                </label>
                <div className="buttons-field">
                  <NavLink
                    className="button is-secondary"
                    to="/connexion"
                  >
                    {'J’ai déjà un compte'}
                  </NavLink>

                  <button
                    className="button is-primary is-outlined"
                    disabled={!valid}
                    type="submit"
                  >
                    {'Créer'}
                  </button>
                </div>
              </form>
            )}
          </Form>
        </div>
      </section>
    )
  }
}

SignupForm.propTypes = {
  closeNotification: PropTypes.func.isRequired,
  createNewProUser: PropTypes.func.isRequired,
  errors: PropTypes.arrayOf(PropTypes.string).isRequired,
  offererName: PropTypes.string.isRequired,
  redirectToConfirmation: PropTypes.func.isRequired,
  showNotification: PropTypes.func.isRequired,
}

export default SignupForm
