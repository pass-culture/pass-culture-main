/*
 * @debt directory "Gaël: this file should be migrated within the new directory structure"
 * @debt deprecated "Gaël: deprecated usage of react-final-form"
 * @debt deprecated "Gaël: deprecated usage of react-final-form custom fields"
 * @debt standard "Gaël: migration from classes components to function components"
 */

import createDecorator from 'final-form-calculate'
import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Field, Form } from 'react-final-form'
import { Link } from 'react-router-dom'

import FieldErrors from 'components/layout/form/FieldErrors'
import PasswordField from 'components/layout/form/fields/PasswordField'
import Icon from 'components/layout/Icon'
import TextInput from 'components/layout/inputs/TextInput/TextInput'
import { LegalInfos } from 'components/layout/LegalInfos/LegalInfos'
import { redirectLoggedUser } from 'components/router/helpers'
import bindAddressAndDesignationFromSiren from 'repository/siren/bindSirenFieldToDesignation'
import { analytics } from 'utils/firebase'

import SirenField from './SirenField/SirenField'

const addressAndDesignationFromSirenDecorator = createDecorator({
  field: 'siren',
  updates: bindAddressAndDesignationFromSiren,
})

const required = value => (value ? undefined : 'Required')

/**
 * @debt standard "Annaëlle: Composant de classe à migrer en fonctionnel"
 */
class SignupForm extends PureComponent {
  constructor(props) {
    super(props)
    const { history, location, currentUser } = props
    redirectLoggedUser(history, location, currentUser)
  }

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
    const script = document.getElementById('hs-script-loader')
    document.body.removeChild(script)
  }

  onHandleSuccess = () => {
    const { redirectToConfirmation } = this.props

    redirectToConfirmation()
  }

  onHandleFail = () => {
    const { notifyError } = this.props

    notifyError('Une ou plusieurs erreurs sont présentes dans le formulaire.')
  }

  handleSubmit = values => {
    const { createNewProUser } = this.props

    createNewProUser(values, this.onHandleFail, this.onHandleSuccess)
  }

  renderEmailTextField = ({ input }) => {
    const { errors } = this.props
    return (
      <TextInput
        error={errors ? errors.email : null}
        label="Adresse e-mail"
        name="email"
        onChange={input.onChange}
        placeholder="nom@exemple.fr"
        required
        value={input.value}
      />
    )
  }

  renderNameTextField = ({ input }) => {
    const { errors } = this.props
    return (
      <TextInput
        error={errors ? errors.lastName : null}
        label="Nom"
        name="lastName"
        onChange={input.onChange}
        placeholder="Mon nom"
        required
        value={input.value}
      />
    )
  }

  renderFirstNameTextField = ({ input }) => {
    const { errors } = this.props
    return (
      <TextInput
        error={errors ? errors.publicName : null}
        label="Prénom"
        name="firstName"
        onChange={input.onChange}
        placeholder="Mon prénom"
        required
        value={input.value}
      />
    )
  }

  renderPhoneNumberField = ({ input }) => {
    const { errors } = this.props
    return (
      <TextInput
        error={errors ? errors.phoneNumber : null}
        label="Téléphone (utilisé uniquement par l’équipe du pass Culture)"
        name="phoneNumber"
        onChange={input.onChange}
        placeholder="Mon numéro de téléphone"
        required
        value={input.value}
      />
    )
  }

  render() {
    const { errors } = this.props

    return (
      <section className="sign-up-form-page">
        <div className="content">
          <h1>Créer votre compte professionnel</h1>
          <h2>
            Merci de compléter les champs suivants pour créer votre compte.
          </h2>
          <div className="sign-up-operating-procedures">
            <div>
              Nous vous invitons à prendre connaissance des modalités de
              fonctionnement avant de renseigner les champs suivants.
            </div>
            <a
              className="tertiary-link"
              href="https://docs.passculture.app/le-pass-culture-en-quelques-mots"
              onClick={() =>
                analytics.logClickFaq(this.props.location.pathname)
              }
              rel="noopener noreferrer"
              target="_blank"
            >
              <Icon svg="ico-external-site" />
              <span>Fonctionnement du pass Culture pro</span>
            </a>
            <a
              className="tertiary-link"
              href="https://passculture.zendesk.com/hc/fr/articles/4411999179665"
              onClick={() =>
                analytics.logClickHelpCenter(this.props.location.pathname)
              }
              rel="noopener noreferrer"
              target="_blank"
            >
              <Icon svg="ico-external-site" />
              <span>Consulter notre centre d’aide</span>
            </a>
          </div>
          <div className="sign-up-tips">
            Tous les champs sont obligatoires sauf mention contraire
          </div>
          <div>{}</div>
          <Form
            decorators={[addressAndDesignationFromSirenDecorator]}
            onSubmit={this.handleSubmit}
          >
            {({ handleSubmit, valid, values }) => (
              <form onSubmit={handleSubmit}>
                <Field
                  component={this.renderEmailTextField}
                  name="email"
                  type="text"
                  validate={required}
                />

                <PasswordField
                  errors={errors ? errors.password : null}
                  label="Mot de passe"
                  name="password"
                  showTooltip
                />

                <Field
                  component={this.renderNameTextField}
                  name="lastName"
                  required
                  validate={required}
                />

                <Field
                  component={this.renderFirstNameTextField}
                  name="firstName"
                  validate={required}
                />

                <Field
                  component={this.renderPhoneNumberField}
                  name="phoneNumber"
                  required
                  validate={required}
                />

                <SirenField value={values.name} />

                <label className="sign-up-checkbox" htmlFor="sign-up-checkbox">
                  <Field
                    component="input"
                    id="sign-up-checkbox"
                    name="contactOk"
                    type="checkbox"
                  />
                  <span>
                    J’accepte d’être contacté par e-mail pour recevoir les
                    nouveautés du pass Culture et contribuer à son amélioration
                    (facultatif)
                  </span>
                  <FieldErrors
                    customMessage={errors ? errors.contactOk : null}
                  />
                </label>
                <LegalInfos
                  className="sign-up-infos-before-signup"
                  pathname={location.pathname}
                  title="Créer mon compte"
                />
                <div className="buttons-field">
                  <Link
                    className="secondary-link"
                    onClick={() => analytics.logClickAlreayAccount()}
                    to="/connexion"
                  >
                    J’ai déjà un compte
                  </Link>
                  <button
                    className="primary-button"
                    disabled={!valid}
                    type="submit"
                  >
                    Créer mon compte
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

SignupForm.defaultProps = {
  currentUser: null,
}

SignupForm.propTypes = {
  createNewProUser: PropTypes.func.isRequired,
  currentUser: PropTypes.shape(),
  errors: PropTypes.shape().isRequired,
  history: PropTypes.func.isRequired,
  location: PropTypes.shape().isRequired,
  notifyError: PropTypes.func.isRequired,
  redirectToConfirmation: PropTypes.func.isRequired,
}

export default SignupForm
