import { Form, Formik } from 'formik'
import React from 'react'
import { useDispatch } from 'react-redux'
import { Link, useLocation } from 'react-router-dom'

import { api } from 'apiClient/api'
import { HTTP_STATUS } from 'apiClient/helpers'
import { BannerRGS } from 'components/Banner'
import FormLayout from 'components/FormLayout'
import { Events } from 'core/FirebaseEvents/constants'
import useActiveFeature from 'hooks/useActiveFeature'
import useAnalytics from 'hooks/useAnalytics'
import useNotification from 'hooks/useNotification'
import { KeyIcon } from 'icons'
import { setCurrentUser } from 'store/user/actions'
import { PasswordInput, SubmitButton, TextInput } from 'ui-kit'
import { UNAVAILABLE_ERROR_PAGE } from 'utils/routes'

import styles from '../Signin.module.scss'

import { SIGNIN_FORM_DEFAULT_VALUES } from './constants'
import { validationSchema } from './validationSchema'

interface ISigninFormValues {
  email: string
  password: string
}

interface ISigninApiErrorResponse {
  status: number
  errors: {
    [key: string]: string
  }
}

const SigninForm = (): JSX.Element => {
  const notification = useNotification()
  const dispatch = useDispatch()
  const location = useLocation()
  const { logEvent } = useAnalytics()
  const isAccountCreationAvailable = useActiveFeature('API_SIRENE_AVAILABLE')

  const accountCreationUrl = isAccountCreationAvailable
    ? '/inscription'
    : UNAVAILABLE_ERROR_PAGE

  const onSubmit = (
    values: ISigninFormValues,
    submitting: (x: boolean) => void
  ) => {
    const { email, password } = values
    api
      .signin({ identifier: email, password })
      .then(user => {
        dispatch(setCurrentUser(user ? user : null))
      })
      .catch(payload => {
        setCurrentUser(null)
        onHandleFail(
          { status: payload.status, errors: payload.body },
          submitting
        )
      })
  }

  const onHandleFail = (
    payload: ISigninApiErrorResponse,
    submitting: (x: boolean) => void
  ) => {
    const { errors, status } = payload
    if (status === HTTP_STATUS.TOO_MANY_REQUESTS) {
      notification.error(
        'Nombre de tentatives de connexion dépassé. Veuillez réessayer dans 1 minute.'
      )
    } else if (errors && Object.values(errors).length > 0) {
      notification.error('Identifiant ou mot de passe incorrect.')
    }
    submitting(false)
  }

  return (
    <>
      <Formik
        initialValues={SIGNIN_FORM_DEFAULT_VALUES}
        onSubmit={(values, { setSubmitting }) =>
          onSubmit(values, setSubmitting)
        }
        validationSchema={validationSchema}
        validateOnChange
      >
        {({ dirty, isValid, isSubmitting }) => (
          <Form>
            <FormLayout>
              <div className={styles['signin-form']}>
                <FormLayout.Row>
                  <TextInput
                    label="Adresse e-mail"
                    name="email"
                    placeholder="email@exemple.com"
                  />
                </FormLayout.Row>
                <FormLayout.Row>
                  <PasswordInput
                    name="password"
                    label="Mot de passe"
                    placeholder="Votre mot de passe"
                  />
                </FormLayout.Row>
              </div>
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
                <KeyIcon className="ico-key" />
                Mot de passe oublié ?
              </Link>
              <div className={styles['buttons-field']}>
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
                <SubmitButton
                  className="primary-button"
                  isLoading={isSubmitting}
                  disabled={!dirty || !isValid}
                >
                  Se connecter
                </SubmitButton>
              </div>
              <BannerRGS />
            </FormLayout>
          </Form>
        )}
      </Formik>
    </>
  )
}

export default SigninForm
