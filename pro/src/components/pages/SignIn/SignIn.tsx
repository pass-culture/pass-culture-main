import React, { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useHistory, useLocation } from 'react-router'

import { BannerRGS } from 'new_components/Banner'
import { Events } from 'core/FirebaseEvents/constants'
import { HTTP_STATUS } from 'api/helpers'
import { Link } from 'react-router-dom'
import Logo from 'components/layout/Logo'
import PageTitle from 'components/layout/PageTitle/PageTitle'
import { PasswordInput } from './PasswordInput'
import { RootState } from 'store/reducers'
import TextInput from 'components/layout/inputs/TextInput/TextInput'
import { UNAVAILABLE_ERROR_PAGE } from 'utils/routes'
import { redirectLoggedUser } from 'components/router/helpers'
import { signin } from 'store/user/thunks'
import useActiveFeature from 'components/hooks/useActiveFeature'
import useCurrentUser from 'components/hooks/useCurrentUser'
import useNotification from 'components/hooks/useNotification'

const SignIn = (): JSX.Element => {
  const [emailValue, setEmailValue] = useState<string>('')
  const [passwordValue, setPasswordValue] = useState<string>('')

  const { currentUser } = useCurrentUser()
  const history = useHistory()
  const location = useLocation()
  const logEvent = useSelector((state: RootState) => state.app.logEvent)
  const dispatch = useDispatch()
  const notification = useNotification()
  const isAccountCreationAvailable = useActiveFeature('API_SIRENE_AVAILABLE')
  const isSubmitButtonDisabled = emailValue === '' || passwordValue === ''

  useEffect(() => {
    redirectLoggedUser(history, location, currentUser)
  }, [currentUser])

  const accountCreationUrl = isAccountCreationAvailable
    ? '/inscription'
    : UNAVAILABLE_ERROR_PAGE

  const handleOnChangeEmail = (event: React.ChangeEvent<HTMLInputElement>) => {
    setEmailValue(event.target.value)
  }

  const handleOnChangePassword = (newPassword: string) => {
    setPasswordValue(newPassword)
  }

  const onHandleSuccessRedirect = () => {
    redirectLoggedUser(history, location, currentUser)
  }

  const onHandleFail = (payload: {
    status: number
    errors: {
      [key: string]: string
    }
  }) => {
    const { errors, status } = payload
    const { password, identifier } = errors
    if (password || identifier) {
      notification.error('Identifiant ou mot de passe incorrect.')
    } else if (status === HTTP_STATUS.TOO_MANY_REQUESTS) {
      notification.error(
        'Nombre de tentatives de connexion dépassé. Veuillez réessayer dans 1 minute.'
      )
    }
  }

  const handleOnSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    return dispatch(
      signin(emailValue, passwordValue, onHandleSuccessRedirect, onHandleFail)
    )
  }

  return (
    <>
      <PageTitle title="Se connecter" />
      <div className="logo-side">
        <Logo noLink signPage />
      </div>
      <section className="scrollable-content-side">
        <div className="content">
          <h1>Bienvenue sur l’espace dédié aux acteurs culturels</h1>
          <h2>
            Et merci de votre participation pour nous aider à l’améliorer !
          </h2>
          <span className="has-text-grey">
            Tous les champs sont obligatoires
          </span>
          <form noValidate onSubmit={handleOnSubmit}>
            <div className="signin-form">
              <TextInput
                label="Adresse e-mail"
                name="identifier"
                onChange={handleOnChangeEmail}
                placeholder="Identifiant (e-mail)"
                required
                type="email"
                value={emailValue}
              />
              <PasswordInput
                onChange={handleOnChangePassword}
                value={passwordValue}
              />
              <Link
                className="tertiary-link"
                id="lostPasswordLink"
                onClick={() =>
                  logEvent(Events.CLICKED_FORGOTTEN_PASSWORD, {
                    from: location.pathname,
                  })
                }
                to="/mot-de-passe-perdu"
              >
                Mot de passe égaré ?
              </Link>
              <BannerRGS />
            </div>
            <div className="field buttons-field">
              <Link
                className="secondary-link"
                onClick={() =>
                  logEvent(Events.CLICKED_CREATE_ACCOUNT, {
                    from: location.pathname,
                  })
                }
                to={accountCreationUrl}
              >
                Créer un compte
              </Link>
              <button
                className="primary-button"
                disabled={isSubmitButtonDisabled}
                id="signin-submit-button"
                type="submit"
              >
                Se connecter
              </button>
            </div>
          </form>
        </div>
      </section>
    </>
  )
}

export default SignIn
