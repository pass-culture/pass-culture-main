import { yupResolver } from '@hookform/resolvers/yup'
import { useEffect, useState } from 'react'
import { FormProvider, useForm } from 'react-hook-form'
import { useDispatch } from 'react-redux'
import { Navigate, useSearchParams } from 'react-router'

import { api } from 'apiClient/api'
import { HTTP_STATUS, isErrorAPIError } from 'apiClient/helpers'
import { Layout } from 'app/App/layout/Layout'
import {
  RECAPTCHA_ERROR,
  RECAPTCHA_ERROR_MESSAGE,
} from 'commons/core/shared/constants'
import { useInitReCaptcha } from 'commons/hooks/useInitReCaptcha'
import { useNotification } from 'commons/hooks/useNotification'
import { useRedirectLoggedUser } from 'commons/hooks/useRedirectLoggedUser'
import { AppDispatch } from 'commons/store/store'
import { updateUser } from 'commons/store/user/reducer'
import { initializeUserThunk } from 'commons/store/user/thunks'
import { getReCaptchaToken } from 'commons/utils/recaptcha'
import { MandatoryInfo } from 'components/FormLayout/FormLayoutMandatoryInfo'

import { SIGNIN_FORM_DEFAULT_VALUES } from './constants'
import { SigninForm } from './SigninForm'
import { validationSchema } from './validationSchema'

export interface SigninFormValues {
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
  const [searchParams, setSearchParams] = useSearchParams()
  const [shouldRedirect, setshouldRedirect] = useState(false)
  const [hasApiError, setHasApiError] = useState(false)
  const dispatch = useDispatch<AppDispatch>()

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

      const result = await dispatch(initializeUserThunk(user)).unwrap()

      if (result.success) {
        setshouldRedirect(true)
      }
    } catch (error) {
      if (isErrorAPIError(error) || error === RECAPTCHA_ERROR) {
        dispatch(updateUser(null))
        if (isErrorAPIError(error)) {
          onHandleFail({ status: error.status, errors: error.body })
        } else {
          notify.error(RECAPTCHA_ERROR_MESSAGE)
        }
      }
    }
  }

  const hookForm = useForm({
    defaultValues: SIGNIN_FORM_DEFAULT_VALUES,
    resolver: yupResolver(validationSchema),
    mode: 'onTouched',
  })

  // This is to reproduce a Formik behavior that reset form error status after an API error
  useEffect(() => {
    const handleClick = () => {
      if (hasApiError) {
        hookForm.clearErrors()
        hookForm.reset({}, { keepValues: true })
        setHasApiError(false)
      }
    }
    document.addEventListener('click', handleClick)
    return () => {
      document.removeEventListener('click', handleClick)
    }
  }, [hookForm, hasApiError])

  const onHandleFail = (payload: SigninApiErrorResponse) => {
    const { errors, status } = payload
    if (status === HTTP_STATUS.TOO_MANY_REQUESTS) {
      notify.error(
        'Nombre de tentatives de connexion dépassé. Veuillez réessayer dans 1 minute.'
      )
    } else if (Object.values(errors).length > 0) {
      hookForm.setError('root', { type: 'apiError' })
      hookForm.setError('email', {
        message: 'Identifiant ou mot de passe incorrect.',
      })
      hookForm.setError('password', {
        message: 'Identifiant ou mot de passe incorrect.',
      })
      setHasApiError(true)
    }
  }

  return shouldRedirect ? (
    <Navigate to="/" replace />
  ) : (
    <Layout layout="sign-up" mainHeading="Connectez-vous">
      <MandatoryInfo areAllFieldsMandatory={true} />
      <FormProvider {...hookForm}>
        <SigninForm onSubmit={hookForm.handleSubmit(onSubmit)} />
      </FormProvider>
    </Layout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = SignIn
