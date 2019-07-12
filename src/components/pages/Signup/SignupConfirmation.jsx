import React from 'react'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'
import { connect } from 'react-redux'
import { ROOT_PATH } from '../../../utils/config'

const SignupConfirmation = () => {
  return (
    <div className="hero">
      <div className="hero-body">
        <div className="is-italic">
          <h1 className="title is-spaced is-1">{"Merci !"}</h1>

          <h2>{"Votre compte est en cours de création."}</h2>
          <h2>
            <span className="is-bold">
              {"Vous allez recevoir un lien de confirmation"}
            </span>{' '}
            {"par e-mail&nbsp;: cliquez sur ce lien pour confirmer la création de votre compte."}
          </h2>
        </div>
        <div className="information-text flex-left">
          <img
            alt="picto info"
            src={`${ROOT_PATH}/icons/picto-info-grey.svg`}
          />
          <p>
            {"Si vous ne recevez pas d'e-mail de notre part d'ici 5 minutes, vérifiez que le message n'est pas dans le dossier \"indésirables\" ou \"spam\" de votre messagerie."}
            <br />
            {"Si vous n’avez rien reçu d’ici demain, merci de "}
            <a href="mailto:pass@culture.gouv.fr?subject=Problème de création de compte pro">
              {"contacter le support"}
            </a>
            {"."}
          </p>
        </div>
      </div>
    </div>
  )
}

export default compose(
  withRouter,
  connect()
)(SignupConfirmation)
