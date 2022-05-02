/* eslint no-undef: 0 */
import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Field, Form } from 'react-final-form'
import { Link } from 'react-router-dom'

import FieldErrors from 'components/layout/form/FieldErrors'
import PasswordField from 'components/layout/form/fields/PasswordField'
import {
  SirenField,
  addressAndDesignationFromSirenDecorator,
} from 'components/layout/form/fields/SirenField'
import TextInput from 'components/layout/inputs/TextInput/TextInput'
import LegalInfos from 'components/layout/LegalInfos/LegalInfos'
import { redirectLoggedUser } from 'components/router/helpers'
import { BannerRGS } from 'new_components/Banner'

import OperatingProcedures from './OperationProcedures'

const required = value => (value ? undefined : 'Required')

/**
 * @debt standard "Annaëlle: Composant de classe à migrer en fonctionnel"
 */
class SignupForm extends PureComponent {
  constructor(props) {
    super(props)
    const { history, location, currentUser } = props
    redirectLoggedUser(history, location, currentUser)
    this.state = {
      errors: {},
    }
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

  onHandleFail = errors => {
    const { notifyError } = this.props
    this.setState({ errors })
    notifyError('Une ou plusieurs erreurs sont présentes dans le formulaire.')
  }

  handleSubmit = values => {
    const { createNewProUser } = this.props
    this.setState({ errors: {} })

    createNewProUser(values, this.onHandleFail, this.onHandleSuccess)
  }

  renderEmailTextField = ({ input }) => {
    const { errors } = this.state
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
    const { errors } = this.state
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
    const { errors } = this.state
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
    const { errors } = this.state
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
    const { errors } = this.state

    return (
      <section className="sign-up-form-page">
        <div className="content">
          <h1>Créer votre compte professionnel</h1>
          <h2>
            Merci de compléter les champs suivants pour créer votre compte.
          </h2>
          <OperatingProcedures />

          <div className="sign-up-tips">
            Tous les champs sont obligatoires sauf mention contraire
          </div>

          <Form
            decorators={[addressAndDesignationFromSirenDecorator]}
            onSubmit={this.handleSubmit}
          >
            {({ handleSubmit, valid, values }) => (
              <form onSubmit={handleSubmit}>
                <div className="sign-up-form">
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

                  <div className="siren-field">
                    <SirenField label="SIREN de la structure que vous représentez" />
                    <span className="field-siren-value">{values.name}</span>
                  </div>

                  <label
                    className="sign-up-checkbox"
                    htmlFor="sign-up-checkbox"
                  >
                    <Field
                      component="input"
                      id="sign-up-checkbox"
                      name="contactOk"
                      type="checkbox"
                    />
                    <span>
                      J’accepte d’être contacté par e-mail pour recevoir les
                      nouveautés du pass Culture et contribuer à son
                      amélioration (facultatif)
                    </span>
                    <FieldErrors
                      customMessage={errors ? errors.contactOk : null}
                    />
                  </label>
                  <LegalInfos
                    className="sign-up-infos-before-signup"
                    title="Créer mon compte"
                  />
                  <BannerRGS />
                </div>
                <div className="buttons-field">
                  <Link className="secondary-link" to="/connexion">
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
  history: PropTypes.func.isRequired,
  location: PropTypes.shape().isRequired,
  notifyError: PropTypes.func.isRequired,
  redirectToConfirmation: PropTypes.func.isRequired,
}

export default SignupForm
