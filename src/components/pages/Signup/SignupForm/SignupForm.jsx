import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import createDecorator from 'final-form-calculate'
import { Link } from 'react-router-dom'
import { Field, Form } from 'react-final-form'

import bindAddressAndDesignationFromSiren from '../../Offerer/OffererCreation/decorators/bindSirenFieldToDesignation'
import PasswordField from '../../../layout/form/fields/PasswordField'
import SirenField from '../../../layout/form/fields/SirenField/SirenField'
import FieldErrors from '../../../layout/form/FieldErrors'
import Icon from '../../../layout/Icon'

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
            {'Créer votre compte professionnel'}
          </h1>
          <h2 className="sign-up-sub-title">
            {'Merci de compléter les champs suivants pour créer votre compte.'}
          </h2>
          <div className="sign-up-operating-procedures">
            <div>
              {
                'Nous vous invitons à prendre connaissance des modalités de fonctionnement avant de renseigner les champs suivants.'
              }
            </div>
            <a
              className="tertiary-link"
              href="https://docs.passculture.app/le-pass-culture-en-quelques-mots"
              rel="noopener noreferrer"
              target="_blank"
            >
              <Icon svg="ico-external-site-red" />
              <span>
                {'Fonctionnement du pass Culture pro'}
              </span>
            </a>
            <a
              className="tertiary-link"
              href="https://aide.passculture.app/fr/article/acteurs-creer-un-compte-professionnel-t0m1hj/"
              rel="noopener noreferrer"
              target="_blank"
            >
              <Icon svg="ico-external-site-red" />
              <span>
                {'Consulter notre centre d’aide'}
              </span>
            </a>
          </div>
          <div className="sign-up-tips">
            <span className="field-asterisk">
              {'*'}
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
            {({ handleSubmit, valid, values }) => (
              <form onSubmit={handleSubmit}>
                <label>
                  {'Adresse e-mail'}
                  <span className="field-asterisk">
                    {'*'}
                  </span>
                  <p className="sub-label">
                    {'...pour se connecter et récupérer son mot de passe en cas d’oubli'}
                  </p>
                  <Field
                    component="input"
                    name="email"
                    placeholder="nom@exemple.fr"
                    required
                    type="text"
                    validate={required}
                  />
                  <FieldErrors customMessage={errors ? errors.email : null} />
                </label>

                <label>
                  {'Mot de passe'}
                  <span className="field-asterisk">
                    {'*'}
                  </span>
                  <span className="sub-label">
                    {'...pour se connecter'}
                  </span>
                  <PasswordField
                    name="password"
                    placeholder="Mon mot de passe"
                    required
                    validate={required}
                  />
                  <FieldErrors customMessage={errors ? errors.password : null} />
                </label>

                <label>
                  {'Nom'}
                  <span className="field-asterisk">
                    {'*'}
                  </span>
                  <Field
                    component="input"
                    name="lastName"
                    placeholder="Mon nom"
                    required
                    validate={required}
                  />
                  <FieldErrors customMessage={errors ? errors.lastName : null} />
                </label>

                <label>
                  {'Prénom'}
                  <span className="field-asterisk">
                    {'*'}
                  </span>
                  <Field
                    component="input"
                    name="firstName"
                    placeholder="Mon prénom"
                    required
                    validate={required}
                  />
                  <FieldErrors customMessage={errors ? errors.firstName : null} />
                  <FieldErrors customMessage={errors ? errors.publicName : null} />
                </label>

                <label>
                  {'Téléphone'}
                  <span className="field-asterisk">
                    {'*'}
                  </span>
                  <p className="sub-label">
                    {'...utilisé uniquement par l’équipe du pass Culture'}
                  </p>
                  <Field
                    component="input"
                    name="phoneNumber"
                    placeholder="Mon numéro de téléphone"
                    required
                    validate={required}
                  />
                  <FieldErrors customMessage={errors ? errors.phoneNumber : null} />
                </label>

                <SirenField
                  subLabel="... de la structure que vous représentez"
                  value={values.name}
                />

                <label className="sign-up-checkbox">
                  <Field
                    component="input"
                    name="contact_ok"
                    required
                    type="checkbox"
                    validate={required}
                  />
                  <span>
                    {
                      'J’accepte d’être contacté par e-mail pour donner mon avis sur le pass Culture'
                    }
                    <span className="field-asterisk">
                      {'*'}
                    </span>
                  </span>
                  <FieldErrors customMessage={errors ? errors.contact_ok : null} />
                </label>

                <div className="sign-up-infos-before-signup">
                  <span>
                    {'En cliquant sur Créer mon compte, vous acceptez nos '}
                  </span>
                  <a
                    className="quaternary-link"
                    href="https://docs.passculture.app/textes-normatifs"
                    rel="noopener noreferrer"
                    target="_blank"
                  >
                    <Icon svg="ico-external-site-red" />
                    <span>
                      {'Conditions Générales d’Utilisation'}
                    </span>
                  </a>
                  <span>
                    {' ainsi que notre '}
                  </span>
                  <a
                    className="quaternary-link"
                    href="https://docs.passculture.app/textes-normatifs/charte-des-donnees-personnelles"
                    rel="noopener noreferrer"
                    target="_blank"
                  >
                    <Icon svg="ico-external-site-red" />
                    <span>
                      {'Charte des Données Personnelles'}
                    </span>
                  </a>
                  <span>
                    {
                      '. Pour en savoir plus sur la gestion de vos données personnelles et pour exercer vos droits, ou répondre à toute autre question, '
                    }
                  </span>
                  <a
                    className="quaternary-link"
                    href="mailto:support@passculture.app"
                    rel="noopener noreferrer"
                    target="_blank"
                  >
                    <Icon svg="ico-email-red" />
                    <span>
                      {'contactez notre support.'}
                    </span>
                  </a>
                </div>
                <div className="buttons-field">
                  <Link
                    className="secondary-link"
                    to="/connexion"
                  >
                    {'J’ai déjà un compte'}
                  </Link>
                  <button
                    className="primary-button"
                    disabled={!valid}
                    type="submit"
                  >
                    {'Créer mon compte'}
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
  errors: PropTypes.shape().isRequired,
  redirectToConfirmation: PropTypes.func.isRequired,
  showNotification: PropTypes.func.isRequired,
}

export default SignupForm
