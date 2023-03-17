import React, { Fragment } from 'react'
import { Link, useLocation } from 'react-router-dom'

import PageTitle from 'components/PageTitle/PageTitle'
import useRedirectLoggedUser from 'hooks/useRedirectLoggedUser'
import Logo from 'ui-kit/Logo/Logo'

const SetPasswordConfirm = () => {
  const location = useLocation()
  const displayErrorMessage =
    location.pathname === '/creation-de-mot-de-passe-erreur'
  useRedirectLoggedUser()

  return (
    <Fragment>
      <PageTitle title="Définition du mot de passe" />
      <div className="logo-side">
        <Logo noLink signPage />
      </div>
      <div className="scrollable-content-side">
        <div className="content" id="override-content-width">
          <section className="password-set-confirm">
            {!displayErrorMessage && (
              <div>
                <h1>Votre mot de passe a bien été enregistré !</h1>
                <h2>
                  Vous pouvez dès à présent vous connecter avec votre mot de
                  passe.
                </h2>

                <Link
                  className="primary-link redirection-button"
                  to="/connexion"
                >
                  Se connecter
                </Link>
              </div>
            )}
            {displayErrorMessage && (
              <div>
                <h1>Votre lien a expiré !</h1>
                <h2>Veuillez contacter notre support</h2>

                <a
                  className="primary-link redirection-button"
                  href="mailto:support-pro@passculture.app"
                  rel="noopener noreferrer"
                  target="_blank"
                >
                  Contacter
                </a>
              </div>
            )}
          </section>
        </div>
      </div>
    </Fragment>
  )
}

export default SetPasswordConfirm
