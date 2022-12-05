import { Form, FormikProvider, useFormik } from 'formik'
import React, { useEffect, useRef } from 'react'
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
import { IcoKey } from 'icons'
import { setCurrentUser } from 'store/user/actions'
import { PasswordInput, SubmitButton, TextInput } from 'ui-kit'
import { UNAVAILABLE_ERROR_PAGE } from 'utils/routes'

import { SIGNIN_FORM_DEFAULT_VALUES } from './constants'
import { ISigninApiErrorResponse, ISigninFormValues } from './types'
import { validationSchema } from './validationSchema'

const SigninForm = (): JSX.Element => {
  const notification = useNotification()
  const dispatch = useDispatch()
  const location = useLocation()
  const { logEvent } = useAnalytics()
  const isAccountCreationAvailable = useActiveFeature('API_SIRENE_AVAILABLE')

  const accountCreationUrl = isAccountCreationAvailable
    ? '/inscription'
    : UNAVAILABLE_ERROR_PAGE

  const onSubmit = (values: ISigninFormValues) => {
    const { email, password } = values
    api
      .signin({ identifier: email, password })
      .then(user => {
        dispatch(setCurrentUser(user ? user : null))
      })
      .catch(payload => {
        setCurrentUser(null)
        onHandleFail({ status: payload.status, errors: payload.body })
      })
  }

  const onHandleFail = (payload: ISigninApiErrorResponse) => {
    const { errors, status } = payload
    if (status === HTTP_STATUS.TOO_MANY_REQUESTS) {
      notification.error(
        'Nombre de tentatives de connexion dépassé. Veuillez réessayer dans 1 minute.'
      )
    } else if (errors && Object.values(errors).length > 0) {
      notification.error('Identifiant ou mot de passe incorrect.')
    }
    formik.setSubmitting(false)
  }

  const formik = useFormik({
    initialValues: SIGNIN_FORM_DEFAULT_VALUES,
    onSubmit: onSubmit,
    validationSchema,
    validateOnChange: false,
  })

  // Track the state of the form when the user gives up
  const touchedRef = useRef(formik.touched)
  const errorsRef = useRef(formik.errors)

  useEffect(() => {
    touchedRef.current = formik.touched
    errorsRef.current = formik.errors
  }, [formik.touched, formik.errors])

  return (
    <>
      <FormikProvider value={formik}>
        <Form onSubmit={formik.handleSubmit}>
          <FormLayout>
            <div className="sign-up-form">
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
                  placeholder="Mon mot de passe"
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
              <IcoKey className="ico-key" /> Mot de passe égaré ?
            </Link>
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
              <SubmitButton
                className="primary-button"
                isLoading={formik.isSubmitting}
                disabled={!formik.dirty || !formik.isValid}
              >
                Se connecter
              </SubmitButton>
            </div>
            <BannerRGS />
          </FormLayout>
        </Form>
      </FormikProvider>
    </>
  )
}

export default SigninForm
