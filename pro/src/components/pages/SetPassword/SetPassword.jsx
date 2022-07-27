import PropTypes from 'prop-types'
import React, { Fragment, useCallback, useState } from 'react'
import { Field, Form } from 'react-final-form'
import { useHistory, useLocation, useRouteMatch } from 'react-router-dom'

import PasswordField from 'components/layout/form/fields/PasswordField'
import LegalInfos from 'components/layout/LegalInfos/LegalInfos'
import Logo from 'components/layout/Logo'
import PageTitle from 'components/layout/PageTitle/PageTitle'
import { redirectLoggedUser } from 'components/router/helpers'
import { setPassword } from 'repository/pcapi/pcapi'

export const INVALID_FORM_MESSAGE =
  "Une erreur s'est produite, veuillez corriger le formulaire."
export const UNKNOWN_ERROR_MESSAGE =
  "Une erreur s'est produite, veuillez contacter le support."
export const DIFFERENT_PASSWORDS_ERROR_MESSAGE =
  'Les deux mots de passe ne sont pas identiques'

export const SetPassword = props => {
  const { currentUser, showNotification } = props
  const history = useHistory()
  const location = useLocation()
  const match = useRouteMatch()

  redirectLoggedUser(history, location, currentUser)

  const redirectOnTokenError = useCallback(() => {
    history.push('/creation-de-mot-de-passe-confirmation?error=unvalid-link')
  }, [history])

  const token = match?.params.token

  if (!token) {
    redirectOnTokenError()
  }

  const [backendErrors, setBackendErrors] = useState(null)

  const submitSetFirstPassword = useCallback(
    values =>
      setPassword(token, values.password)
        .then(() => {
          history.push('/creation-de-mot-de-passe-confirmation')
        })
        .catch(error => {
          if (error.errors.newPassword) {
            showNotification('error', INVALID_FORM_MESSAGE)
            setBackendErrors(error.errors)
            return
          }
          if (error.errors.token) {
            redirectOnTokenError()
            return
          }
          showNotification('error', UNKNOWN_ERROR_MESSAGE)
        }),
    [showNotification, history, token, redirectOnTokenError]
  )

  const getPasswordErrors = useCallback(
    errors => {
      if (errors?.password && errors.password !== true) {
        return errors.password
      }

      if (backendErrors?.newPassword) {
        return backendErrors.newPassword
      }

      return null
    },
    [backendErrors]
  )

  const validateForm = useCallback(values => {
    const errors = {}
    if (values.passwordConfirmation !== values.password) {
      errors.passwordConfirmation = [DIFFERENT_PASSWORDS_ERROR_MESSAGE]
    }
    return errors
  }, [])

  return (
    <Fragment>
      <PageTitle title="Définition du mot de passe" />
      <div className="logo-side">
        <Logo noLink signPage />
      </div>
      <div className="scrollable-content-side">
        <div className="content" id="override-content-width">
          {token && (
            <section className="password-set-request-form">
              <div>
                <h1>Bienvenue sur l’espace dédié aux acteurs culturels</h1>
                <h2>
                  Pour accéder à votre espace, merci de définir votre mot de
                  passe.
                </h2>
                <Form onSubmit={submitSetFirstPassword} validate={validateForm}>
                  {({ handleSubmit, errors }) => (
                    <form className="set-password-form" onSubmit={handleSubmit}>
                      <PasswordField
                        errors={getPasswordErrors(errors)}
                        label="Mot de passe"
                        name="password"
                        showTooltip
                      />
                      <PasswordField
                        errors={errors?.passwordConfirmation}
                        label="Confirmer le mot de passe"
                        name="passwordConfirmation"
                      />
                      <label
                        className="sign-up-checkbox"
                        htmlFor="sign-up-checkbox"
                      >
                        <Field
                          component="input"
                          id="sign-up-checkbox"
                          name="contact_ok"
                          type="checkbox"
                        />
                        <span>
                          J’accepte d’être contacté par e-mail pour donner mon
                          avis sur le pass Culture
                        </span>
                      </label>
                      <LegalInfos
                        className="set-password-legal-infos"
                        title="Envoyer"
                      />

                      <button
                        className="primary-button submit-button password-set-button"
                        type="submit"
                      >
                        Envoyer
                      </button>
                    </form>
                  )}
                </Form>
              </div>
            </section>
          )}
        </div>
      </div>
    </Fragment>
  )
}

SetPassword.defaultProps = {
  currentUser: null,
}

SetPassword.propTypes = {
  currentUser: PropTypes.shape(),
  showNotification: PropTypes.func.isRequired,
}
