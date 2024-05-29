import { FormikProvider, useFormik } from 'formik'
import React, { useEffect } from 'react'
import { useDispatch } from 'react-redux'
import { Navigate, useSearchParams } from 'react-router-dom'

import { api } from 'apiClient/api'
import { HTTP_STATUS, isErrorAPIError } from 'apiClient/helpers'
import { AppLayout } from 'app/AppLayout'
import { useInitReCaptcha } from 'hooks/useInitReCaptcha'
import { useNotification } from 'hooks/useNotification'
import { useRedirectLoggedUser } from 'hooks/useRedirectLoggedUser'
import logoPassCultureProFullIcon from 'icons/logo-pass-culture-pro-full.svg'
import { CookiesFooter } from 'pages/CookiesFooter/CookiesFooter'
import { updateUser } from 'store/user/reducer'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { getReCaptchaToken } from 'utils/recaptcha'

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
    const captchaToken = await getReCaptchaToken('loginUser')
    const { email, password } = values
    try {
      const user = await api.signin({
        identifier: email,
        password,
        captchaToken,
      })
      dispatch(updateUser(user))
      setshouldRedirect(true)
    } catch (error) {
      if (isErrorAPIError(error)) {
        updateUser(null)
        onHandleFail({ status: error.status, errors: error.body })
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
    <AppLayout layout="without-nav">
      <header className={styles['logo-side']}>
        <SvgIcon
          className="logo-unlogged"
          viewBox="0 0 282 120"
          alt="Pass Culture pro, l’espace des acteurs culturels"
          src={logoPassCultureProFullIcon}
          width="135"
        />
      </header>
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
        <CookiesFooter className={styles['cookies-footer']} />
      </section>
    </AppLayout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = SignIn
