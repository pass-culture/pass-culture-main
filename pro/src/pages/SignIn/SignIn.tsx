import { yupResolver } from '@hookform/resolvers/yup'
import { useEffect, useState } from 'react'
import { FormProvider, useForm } from 'react-hook-form'
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
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { useInitReCaptcha } from 'commons/hooks/useInitReCaptcha'
import { useNotification } from 'commons/hooks/useNotification'
import { useRedirectLoggedUser } from 'commons/hooks/useRedirectLoggedUser'
import {
  updateOffererIsOnboarded,
  updateOffererNames,
  updateSelectedOffererId,
} from 'commons/store/offerer/reducer'
import { updateUser } from 'commons/store/user/reducer'
import { getReCaptchaToken } from 'commons/utils/recaptcha'
import { storageAvailable } from 'commons/utils/storageAvailable'
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
  const dispatch = useDispatch()
  const [searchParams, setSearchParams] = useSearchParams()
  const [shouldRedirect, setshouldRedirect] = useState(false)
  const [hasApiError, setHasApiError] = useState(false)

  const is2025SignUpEnabled = useActiveFeature('WIP_2025_SIGN_UP')

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

      const initializeOffererIsOnboarded = async (offererId: number) => {
        try {
          const response = await api.getOfferer(offererId)
          dispatch(updateOffererIsOnboarded(response.isOnboarded))
        } catch (e: unknown) {
          if (isErrorAPIError(e) && e.status === 403) {
            // Do nothing at this point,
            // Because a 403 means that the user is waiting for a "rattachement" to the offerer,
            // But we must let him sign in
            return
          }
          // Else it's another error we should handle here at sign in
          throw e
        }
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
          await initializeOffererIsOnboarded(
            savedOffererId ? Number(savedOffererId) : firstOffererId
          )
        } else {
          dispatch(updateSelectedOffererId(firstOffererId))
          await initializeOffererIsOnboarded(firstOffererId)
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
    <Layout
      layout={is2025SignUpEnabled ? 'sign-up' : 'logged-out'}
      mainHeading={
        is2025SignUpEnabled
          ? 'Connexion'
          : 'Bienvenue sur l’espace partenaires culturels'
      }
    >
      <MandatoryInfo areAllFieldsMandatory={true} />
      <FormProvider {...hookForm}>
        <SigninForm onSubmit={hookForm.handleSubmit(onSubmit)} />
      </FormProvider>
    </Layout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = SignIn
