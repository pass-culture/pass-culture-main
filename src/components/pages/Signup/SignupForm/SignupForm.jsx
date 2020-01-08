import PropTypes from 'prop-types'
import React, { Fragment, PureComponent } from 'react'
import { NavLink } from 'react-router-dom'
import { Field, Form, SubmitButton } from 'pass-culture-shared'
import { CGU_URL } from '../../../../utils/config'

class SignupForm extends PureComponent {
  onHandleSuccessRedirect = () => '/inscription/confirmation'

  onHandleFormatPatch = patch => Object.assign({ publicName: patch.firstName }, patch)

  isFieldDisabling = offererName => () => !offererName

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

  renderPasswordTooltip = () => {
    return `
          <Fragment>Votre mot de passe doit contenir au moins :
            <ul>
              <li>12 caractères</li>
              <li>une majuscule et une minuscule</li>
              <li>un chiffre</li>
              <li>un caractère spécial (signe de ponctuation, symbole monétaire ou mathématique)</li>
            </ul>
          </Fragment>`
  }

  render() {
    const { errors, patch, offererName } = this.props

    return (
      <section>
        <div className="hero-body">
          <h1 className="title is-spaced is-1">
            {'Créez votre compte'}
          </h1>
          <h2 className="subtitle is-2">
            {'Nous vous invitons à prendre connaissance des '}
            <a
              className="is-secondary"
              href="https://pass.culture.fr/ressources"
              rel="noopener noreferrer"
              target="_blank"
            >
              {'modalités de fonctionnement en cliquant ici '}
            </a>
            {'avant de renseigner les champs suivants.'}
          </h2>
          <span className="has-text-grey">
            <span className="required-legend">
              {'*'}
            </span>
            {' Champs obligatoires'}
          </span>
          <Form
            action="/users/signup/pro"
            BlockComponent={null}
            formatPatch={this.onHandleFormatPatch}
            handleSuccessNotification={null}
            handleSuccessRedirect={this.onHandleSuccessRedirect}
            layout="vertical"
            name="user"
            patch={patch}
          >
            <div className="field-group">
              <Field
                label="Adresse e-mail"
                name="email"
                placeholder="nom@exemple.fr"
                required
                sublabel="pour se connecter et récupérer son mot de passe en cas d’oubli"
                type="email"
              />
              <Field
                info={this.renderPasswordTooltip()}
                label="Mot de passe"
                name="password"
                placeholder="Mon mot de passe"
                required
                sublabel="pour se connecter"
                type="password"
              />
              <Field
                label="Nom"
                name="lastName"
                placeholder="Mon nom"
                required
              />
              <Field
                label="Prénom"
                name="firstName"
                placeholder="Mon prénom"
                required
              />
              <Field
                label="Téléphone"
                name="phoneNumber"
                placeholder="Mon numéro de téléphone"
                required
                sublabel="utilisé uniquement par l'équipe du pass Culture"
              />
              <Field
                disabling={this.isFieldDisabling(offererName)}
                label="SIREN"
                name="siren"
                placeholder="123 456 789"
                required
                sublabel="de la structure que vous représentez"
                type="siren"
                withFetchedName
              />
              <Field
                label="Je souhaite recevoir les actualités du pass Culture"
                name="newsletter_ok"
                type="checkbox"
              />
              <Field
                label="J’accepte d'être contacté par e-mail pour donner mon avis sur le pass Culture"
                name="contact_ok"
                required
                type="checkbox"
              />
              <Field
                className="cgu-field"
                label={this.renderCguContent()}
                name="cgu_ok"
                required
                type="checkbox"
              />
              <div className="errors">
                {errors}
              </div>
            </div>
            <div className="buttons-field">
              <NavLink
                className="button is-secondary"
                to="/connexion"
              >
                {'J’ai déjà un compte'}
              </NavLink>
              <SubmitButton
                className="button is-primary is-outlined"
                type="submit"
              >
                {'Créer'}
              </SubmitButton>
            </div>
          </Form>
        </div>
      </section>
    )
  }
}

SignupForm.propTypes = {
  errors: PropTypes.arrayOf(PropTypes.string).isRequired,
  offererName: PropTypes.string.isRequired,
  patch: PropTypes.shape().isRequired,
}

export default SignupForm
