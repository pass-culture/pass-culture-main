import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'

import Logo from 'components/layout/Logo'
import PageTitle from 'components/layout/PageTitle/PageTitle'
import { redirectLoggedUser } from 'components/router/helpers'
import Hero from 'ui-kit/Hero'

import { initReCaptchaScript } from '../../../utils/recaptcha'

import ChangePasswordForm from './ChangePasswordForm'
import ChangePasswordRequestForm from './ChangePasswordRequestForm'

/**
 * @debt standard "Annaëlle: Composant de classe à migrer en fonctionnel"
 */
class LostPassword extends PureComponent {
  constructor(props) {
    super(props)
    const { currentUser, history, location } = props

    redirectLoggedUser(history, location, currentUser)

    this.state = {
      emailValue: '',
      newPasswordErrorMessage: '',
    }
  }

  componentDidMount() {
    this.gcaptchaScript = initReCaptchaScript()
  }

  componentWillUnmount() {
    this.gcaptchaScript.remove()
  }

  redirectToResetPasswordSuccessPage = () => {
    const { history } = this.props
    history.push('/mot-de-passe-perdu?change=1')
  }

  displayPasswordResetErrorMessages = (state, action) => {
    const { showErrorNotification } = this.props
    if (action.payload.errors.newPassword) {
      this.setState({
        newPasswordErrorMessage: action.payload.errors.newPassword[0],
      })
    } else {
      showErrorNotification(
        "Une erreur s'est produite, veuillez réessayer ultérieurement."
      )
    }
  }

  redirectToResetPasswordRequestSuccessPage = () => {
    const { history } = this.props
    history.push('/mot-de-passe-perdu?envoye=1')
  }

  displayPasswordResetRequestErrorMessage = () => {
    const { showErrorNotification } = this.props
    showErrorNotification(
      'Un problème est survenu pendant la réinitialisation du mot de passe, veuillez réessayer plus tard.'
    )
  }

  submitResetPasswordRequest = event => {
    event.preventDefault()
    const { submitResetPasswordRequest } = this.props
    const { emailValue } = this.state

    return submitResetPasswordRequest(
      emailValue,
      this.redirectToResetPasswordRequestSuccessPage,
      this.displayPasswordResetRequestErrorMessage
    )
  }

  submitResetPassword = values => {
    const { submitResetPassword, token } = this.props
    const { newPasswordValue } = values

    return submitResetPassword(
      newPasswordValue,
      token,
      this.redirectToResetPasswordSuccessPage,
      this.displayPasswordResetErrorMessages
    )
  }

  handleInputEmailChange = event => {
    this.setState({ emailValue: event.target.value })
  }

  isResetPasswordRequestSubmitDisabled = () => {
    const { emailValue } = this.state

    return emailValue === ''
  }

  isResetPasswordSubmitDisabled = values => {
    if (!values.newPasswordValue) {
      return true
    }

    return values.newPasswordValue === ''
  }

  render() {
    const { emailValue, newPasswordErrorMessage } = this.state
    const { change, envoye, token } = this.props

    return (
      <>
        <PageTitle title="Mot de passe perdu" />
        <div className="logo-side">
          <Logo noLink signPage />
        </div>
        <div className="scrollable-content-side">
          <div className="content">
            {change && (
              <Hero
                linkLabel="Se connecter"
                linkTo="/connexion"
                text="Vous pouvez dès à présent vous connecter avec votre nouveau mot de passe"
                title="Mot de passe changé !"
              />
            )}
            {envoye && (
              <Hero
                linkLabel="Revenir à l’accueil"
                linkTo="/"
                text="Vous allez recevoir par e-mail les instructions pour définir un nouveau mot de passe."
                title="Merci !"
              />
            )}
            {token && (
              <ChangePasswordForm
                isChangePasswordSubmitDisabled={
                  this.isResetPasswordSubmitDisabled
                }
                newPasswordErrorMessage={newPasswordErrorMessage}
                onSubmit={this.submitResetPassword}
              />
            )}
            {!token && !envoye && !change && (
              <ChangePasswordRequestForm
                emailValue={emailValue}
                isChangePasswordRequestSubmitDisabled={
                  this.isResetPasswordRequestSubmitDisabled
                }
                onChange={this.handleInputEmailChange}
                onSubmit={this.submitResetPasswordRequest}
              />
            )}
          </div>
        </div>
      </>
    )
  }
}

LostPassword.defaultProps = {
  currentUser: null,
}

LostPassword.propTypes = {
  change: PropTypes.bool.isRequired,
  currentUser: PropTypes.shape(),
  envoye: PropTypes.bool.isRequired,
  history: PropTypes.shape().isRequired,
  location: PropTypes.shape().isRequired,
  showErrorNotification: PropTypes.func.isRequired,
  submitResetPassword: PropTypes.func.isRequired,
  submitResetPasswordRequest: PropTypes.func.isRequired,
  token: PropTypes.string.isRequired,
}

export default LostPassword
