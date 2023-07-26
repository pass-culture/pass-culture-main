import { Form, Formik } from 'formik'
import React from 'react'
import { useDispatch } from 'react-redux'
import { useLocation } from 'react-router-dom'

import { api } from 'apiClient/api'
import { HTTP_STATUS } from 'apiClient/helpers'
import { BannerRGS } from 'components/Banner'
import FormLayout from 'components/FormLayout'
import { Events } from 'core/FirebaseEvents/constants'
import useActiveFeature from 'hooks/useActiveFeature'
import useAnalytics from 'hooks/useAnalytics'
import useNotification from 'hooks/useNotification'
import fullKeyIcon from 'icons/full-key.svg'
import { setCurrentUser } from 'store/user/actions'
import { ButtonLink, PasswordInput, SubmitButton, TextInput } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { UNAVAILABLE_ERROR_PAGE } from 'utils/routes'

import styles from '../Signin.module.scss'

import { SIGNIN_FORM_DEFAULT_VALUES } from './constants'
import { validationSchema } from './validationSchema'

interface SigninFormValues {
  email: string
  password: string
}

interface SigninApiErrorResponse {
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
    values: SigninFormValues,
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
    payload: SigninApiErrorResponse,
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
              <FormLayout.Row>
                <TextInput
                  label="Adresse email"
                  name="email"
                  placeholder="email@exemple.com"
                />
              </FormLayout.Row>
              <FormLayout.Row>
                <PasswordInput name="password" label="Mot de passe" />
              </FormLayout.Row>
              <ButtonLink
                icon={fullKeyIcon}
                variant={ButtonVariant.TERNARY}
                link={{
                  to: '/demande-mot-de-passe',
                  isExternal: false,
                }}
                onClick={() =>
                  logEvent?.(Events.CLICKED_FORGOTTEN_PASSWORD, {
                    from: location.pathname,
                  })
                }
              >
                Mot de passe oublié ?
              </ButtonLink>
              <div className={styles['buttons-field']}>
                <ButtonLink
                  className={styles['buttons']}
                  variant={ButtonVariant.SECONDARY}
                  link={{
                    to: accountCreationUrl,
                    isExternal: false,
                  }}
                  onClick={() =>
                    logEvent?.(Events.CLICKED_CREATE_ACCOUNT, {
                      from: location.pathname,
                    })
                  }
                >
                  Créer un compte
                </ButtonLink>
                <SubmitButton
                  className={styles['buttons']}
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
