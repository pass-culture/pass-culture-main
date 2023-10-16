import { FormikProvider, useFormik } from 'formik'
import React, { useEffect } from 'react'
import { useDispatch } from 'react-redux'
import { useSearchParams } from 'react-router-dom'

import { api } from 'apiClient/api'
import { HTTP_STATUS, isErrorAPIError } from 'apiClient/helpers'
import AppLayout from 'app/AppLayout'
import SkipLinks from 'components/SkipLinks'
import useNotification from 'hooks/useNotification'
import useRedirectLoggedUser from 'hooks/useRedirectLoggedUser'
import logoPassCultureProFullIcon from 'icons/logo-pass-culture-pro-full.svg'
import CookiesFooter from 'pages/CookiesFooter/CookiesFooter'
import { setCurrentUser } from 'store/user/actions'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import { SIGNIN_FORM_DEFAULT_VALUES } from './constants'
import styles from './Signin.module.scss'
import SigninForm from './SigninForm'
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

const SignIn = (): JSX.Element => {
  useRedirectLoggedUser()
  const notify = useNotification()
  const dispatch = useDispatch()
  const [searchParams, setSearchParams] = useSearchParams()

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
      const user = await api.signin({ identifier: email, password })
      dispatch(setCurrentUser(user))
    } catch (error) {
      if (isErrorAPIError(error)) {
        setCurrentUser(null)
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
    } else if (errors && Object.values(errors).length > 0) {
      notify.error('Identifiant ou mot de passe incorrect.')
      formik.setStatus('apiError')
      formik.setFieldError('email', 'Identifiant ou mot de passe incorrect.')
      formik.setFieldError('password', 'Identifiant ou mot de passe incorrect.')
    }
  }

  return (
    <>
      <SkipLinks displayMenu={false} />
      <div className={styles['sign-in']}>
        <header className={styles['logo-side']}>
          <SvgIcon
            className="logo-unlogged"
            viewBox="0 0 282 120"
            alt="Pass Culture pro, l'espace des acteurs culturels"
            src={logoPassCultureProFullIcon}
            width="135"
          />
        </header>
        <AppLayout
          layoutConfig={{
            fullscreen: true,
            pageName: 'sign-in',
          }}
        >
          <section className={styles['content']}>
            <h1>Bienvenue sur l’espace dédié aux acteurs culturels</h1>
            <div className={styles['mandatory']}>
              Tous les champs sont obligatoires
            </div>
            <FormikProvider value={formik}>
              <SigninForm />
            </FormikProvider>
            <CookiesFooter className={styles['cookies-footer']} />
          </section>
        </AppLayout>
      </div>
    </>
  )
}

export default SignIn
