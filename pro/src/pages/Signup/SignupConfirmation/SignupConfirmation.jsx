import React from 'react'

import { ROOT_PATH } from 'utils/config'

const SignupConfirmation = () => (
  <section className="sign-up-confirmation-page">
    <div className="content">
      <div className="hero">
        <div className="hero-body">
          <div>
            <h1>Merci !</h1>
            <div className="confirmation-text">
              Votre compte est en cours de création.
            </div>
            <div className="confirmation-text">
              <span>Vous allez recevoir un lien de confirmation</span> par
              e-mail : cliquez sur ce lien pour confirmer la création de votre
              compte.
            </div>
          </div>
          <div className="information-text flex-left">
            <img
              alt="information"
              src={`${ROOT_PATH}/icons/picto-info-grey.svg`}
            />
            <p>
              Si vous ne recevez pas d’e-mail de notre part d’ici 5 minutes,
              vérifiez que le message n’est pas dans le dossier
              {' "'}
              indésirables
              {'" '}
              ou
              {' "'}
              spam
              {'" '}
              de votre messagerie.
              <br />
              Si vous n’avez rien reçu d’ici demain, merci de{' '}
              <a
                className="quaternary-link"
                href="mailto:support-pro@passculture.app?subject=Problème de création de compte pro"
              >
                contacter le support
              </a>
              .
            </p>
          </div>
        </div>
      </div>
    </div>
  </section>
)

export default SignupConfirmation
