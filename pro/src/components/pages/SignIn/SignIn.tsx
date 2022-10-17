import React, { useEffect, useState } from 'react'
import { useDispatch } from 'react-redux'
import { useHistory, useLocation } from 'react-router'
import { Link } from 'react-router-dom'

import { api } from 'apiClient/api'
import { HTTP_STATUS } from 'apiClient/helpers'
import TextInput from 'components/layout/inputs/TextInput/TextInput'
import Logo from 'components/layout/Logo'
import PageTitle from 'components/layout/PageTitle/PageTitle'
import { redirectLoggedUser } from 'components/router/helpers'
import { Events } from 'core/FirebaseEvents/constants'
import useActiveFeature from 'hooks/useActiveFeature'
import useAnalytics from 'hooks/useAnalytics'
import useCurrentUser from 'hooks/useCurrentUser'
import useNotification from 'hooks/useNotification'
import { BannerRGS } from 'new_components/Banner'
import { setCurrentUser } from 'store/user/actions'
import { UNAVAILABLE_ERROR_PAGE } from 'utils/routes'

import { PasswordInput } from './PasswordInput'

const SignIn = (): JSX.Element => {
  const [emailValue, setEmailValue] = useState<string>('')
  const [passwordValue, setPasswordValue] = useState<string>('')

  const { currentUser } = useCurrentUser()
  const history = useHistory()
  const location = useLocation()
  const { logEvent } = useAnalytics()
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
    if (status === HTTP_STATUS.TOO_MANY_REQUESTS) {
      notification.error(
        'Nombre de tentatives de connexion dépassé. Veuillez réessayer dans 1 minute.'
      )
    } else if (errors && Object.values(errors).length > 0) {
      notification.error('Identifiant ou mot de passe incorrect.')
    }
  }

  const handleOnSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    return api
      .signin({ identifier: emailValue, password: passwordValue })
      .then(user => {
        dispatch(setCurrentUser(user ? user : null))
        onHandleSuccessRedirect()
      })
      .catch(payload => {
        setCurrentUser(null)
        onHandleFail({ status: payload.status, errors: payload.body })
      })
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
                placeholder="email@exemple.com"
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
                  logEvent?.(Events.CLICKED_FORGOTTEN_PASSWORD, {
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
                  logEvent?.(Events.CLICKED_CREATE_ACCOUNT, {
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
