import PropTypes from 'prop-types'
import React, { Fragment } from 'react'
import { Link } from 'react-router-dom'

import Logo from 'components/layout/Logo'
import PageTitle from 'components/layout/PageTitle/PageTitle'
import { redirectLoggedUser } from 'components/router/helpers'

export const SetPasswordConfirm = props => {
  const { currentUser, history } = props

  redirectLoggedUser(history, currentUser)

  return (
    <Fragment>
      <PageTitle title="Définition du mot de passe" />
      <div className="logo-side">
        <Logo
          noLink
          signPage
        />
      </div>
      <div className="scrollable-content-side">
        <div
          className="content"
          id="override-content-width"
        >
          <section className="password-set-confirm">
            <div>
              <h1>
                {'Votre mot de passe a bien été enregistré !'}
              </h1>
              <h2>
                {'Vous pouvez dès à présent vous connecter avec votre mot de passe.'}
              </h2>

              <Link
                className="primary-link redirection-button"
                to="/connexion"
              >
                {'Se connecter'}
              </Link>
            </div>
          </section>
        </div>
      </div>
    </Fragment>
  )
}

SetPasswordConfirm.defaultProps = {
  currentUser: null,
}

SetPasswordConfirm.propTypes = {
  currentUser: PropTypes.shape(),
  history: PropTypes.shape().isRequired,
}
