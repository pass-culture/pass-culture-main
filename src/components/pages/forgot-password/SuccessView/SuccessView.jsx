import PropTypes from 'prop-types'
import React, { PureComponent, Fragment } from 'react'

import FormFooter from '../../../forms/FormFooter'

const retryLink = {
  className: 'is-white-text',
  disabled: false,
  label: 'Recommencer',
  url: '/mot-de-passe-perdu',
}

const signInLink = {
  className: 'is-bold is-white-text',
  id: 'success-view-submit',
  disabled: false,
  label: 'Connexion',
  url: '/connexion',
}

class SuccessView extends PureComponent {
  renderRequestSuccessMessage = () => (
    <Fragment>
      <p className="is-medium">
        {'Tu vas recevoir un e-mail avec les instructions de réinitialisation.'}
      </p>
      <p className="is-medium mt28">
        {
          'Si tu n’as rien reçu d’ici une heure, merci de vérifier ton e-mail et de le saisir à nouveau.'
        }
      </p>
    </Fragment>
  )

  renderResetSuccessMessage = () => (
    <p className="is-medium">
      {'Ton mot de passe a bien été enregistré, tu peux l’utiliser pour te connecter'}
    </p>
  )

  render() {
    const { token } = this.props
    const renderSuccessMessage = token
      ? this.renderResetSuccessMessage
      : this.renderRequestSuccessMessage

    return (
      <div className="logout-form-container">
        <div className="is-italic fs22">
          {renderSuccessMessage()}
        </div>
        <FormFooter internalLinks={token ? [signInLink] : [retryLink, signInLink]} />
      </div>
    )
  }
}

SuccessView.defaultProps = {
  token: null,
}

SuccessView.propTypes = {
  token: PropTypes.string,
}

export default SuccessView
