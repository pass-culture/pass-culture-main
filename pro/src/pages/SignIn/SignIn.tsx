import { FormikProvider, useFormik } from 'formik'
import React, { useEffect } from 'react'
import { useDispatch } from 'react-redux'
import { Navigate, useSearchParams } from 'react-router-dom'

import { api } from 'apiClient/api'
import { HTTP_STATUS, isErrorAPIError } from 'apiClient/helpers'
import { Layout } from 'app/App/layout/Layout'
import {
  RECAPTCHA_ERROR,
  RECAPTCHA_ERROR_MESSAGE,
  SAVED_OFFERER_ID_KEY,
} from 'commons/core/shared/constants'
import { useInitReCaptcha } from 'commons/hooks/useInitReCaptcha'
import { useNotification } from 'commons/hooks/useNotification'
import { useRedirectLoggedUser } from 'commons/hooks/useRedirectLoggedUser'
import {
  updateOffererNames,
  updateSelectedOffererId,
  updateOffererIsOnboarded,
} from 'commons/store/offerer/reducer'
import { updateUser } from 'commons/store/user/reducer'
import { getReCaptchaToken } from 'commons/utils/recaptcha'
import { storageAvailable } from 'commons/utils/storageAvailable'

import { SIGNIN_FORM_DEFAULT_VALUES } from './constants'
import styles from './Signin.module.scss'
import { SigninForm } from './SigninForm'
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

export const SignIn = (): JSX.Element => {
  useRedirectLoggedUser()
  const notify = useNotification()
  const dispatch = useDispatch()
  const [searchParams, setSearchParams] = useSearchParams()
  const [shouldRedirect, setshouldRedirect] = React.useState(false)
  useInitReCaptcha()

  useEffect(() => {
    if (searchParams.get('accountValidation') === 'true') {
      notify.success(
        'Votre compte a été créé. Vous pouvez vous connecter avec les identifiants que vous avez choisis.'
      )
      setSearchParams('')
    } else if (
      searchParams.get('accountValidation') === 'false' &&
      searchParams.get('message')
    ) {
      notify.error(searchParams.get('message'))
      setSearchParams('')
    }
  }, [searchParams])

  const onSubmit = async (values: SigninFormValues) => {
    const { email, password } = values
    try {
      const captchaToken = await getReCaptchaToken('loginUser')
      const user = await api.signin({
        identifier: email,
        password,
        captchaToken,
      })

      const inisializeOffererIsOnboarded = async (offererId: number) => {
        const response = await api.getOfferer(offererId)
        dispatch(updateOffererIsOnboarded(response.isOnboarded))
      }

      const offerers = await api.listOfferersNames()
      const firstOffererId = offerers.offerersNames[0]?.id

      if (firstOffererId) {
        dispatch(updateOffererNames(offerers.offerersNames))

        if (storageAvailable('localStorage')) {
          const savedOffererId = localStorage.getItem(SAVED_OFFERER_ID_KEY)
          dispatch(
            updateSelectedOffererId(
              savedOffererId ? Number(savedOffererId) : firstOffererId
            )
          )
          await inisializeOffererIsOnboarded(
            savedOffererId ? Number(savedOffererId) : firstOffererId
          )
        } else {
          dispatch(updateSelectedOffererId(firstOffererId))
          await inisializeOffererIsOnboarded(firstOffererId)
        }
      }

      dispatch(updateUser(user))
      setshouldRedirect(true)
    } catch (error) {
      if (isErrorAPIError(error) || error === RECAPTCHA_ERROR) {
        updateUser(null)
        if (isErrorAPIError(error)) {
          onHandleFail({ status: error.status, errors: error.body })
        } else {
          notify.error(RECAPTCHA_ERROR_MESSAGE)
        }
      }
    }
  }

  const formik = useFormik({
    initialValues: SIGNIN_FORM_DEFAULT_VALUES,
    onSubmit: (values) => onSubmit(values),
    validationSchema,
    validateOnChange: true,
  })

  const onHandleFail = (payload: SigninApiErrorResponse) => {
    const { errors, status } = payload
    if (status === HTTP_STATUS.TOO_MANY_REQUESTS) {
      notify.error(
        'Nombre de tentatives de connexion dépassé. Veuillez réessayer dans 1 minute.'
      )
    } else if (Object.values(errors).length > 0) {
      notify.error('Identifiant ou mot de passe incorrect.')
      formik.setStatus('apiError')
      formik.setFieldError('email', 'Identifiant ou mot de passe incorrect.')
      formik.setFieldError('password', 'Identifiant ou mot de passe incorrect.')
    }
  }

  return shouldRedirect ? (
    <Navigate to="/" replace />
  ) : (
    <Layout layout="logged-out">
      <section className={styles['content']}>
        <h1 className={styles['title']}>
          Bienvenue sur l’espace dédié aux acteurs culturels
        </h1>

        <div className={styles['mandatory']}>
          Tous les champs suivis d’un * sont obligatoires.
        </div>
        <FormikProvider value={formik}>
          <SigninForm />
        </FormikProvider>
      </section>
    </Layout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = SignIn
