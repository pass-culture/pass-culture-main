import { api } from 'apiClient/api'
import { isErrorAPIError } from 'apiClient/helpers'
import { ProUserCreationBodyV2Model } from 'apiClient/v1'
import { yupResolver } from '@hookform/resolvers/yup'
import { useAnalytics } from 'app/App/analytics/firebase'
import { Events } from 'commons/core/FirebaseEvents/constants'
import {
  RECAPTCHA_ERROR,
  RECAPTCHA_ERROR_MESSAGE,
} from 'commons/core/shared/constants'
import { useInitReCaptcha } from 'commons/hooks/useInitReCaptcha'
import { useLogEventOnUnload } from 'commons/hooks/useLogEventOnUnload'
import { useNotification } from 'commons/hooks/useNotification'
import { useRedirectLoggedUser } from 'commons/hooks/useRedirectLoggedUser'
import { getReCaptchaToken } from 'commons/utils/recaptcha'
import { MandatoryInfo } from 'components/FormLayout/FormLayoutMandatoryInfo'
import { useEffect, useRef } from 'react'
import { FormProvider, useForm } from 'react-hook-form'
import { useNavigate } from 'react-router'

import { SIGNUP_FORM_DEFAULT_VALUES } from './constants'
import { OperatingProcedures } from './OperationProcedures/OperationProcedures'
import styles from './SignupContainer.module.scss'
import { SignupForm } from './SignupForm'
import { validationSchema } from './validationSchema'

export const SignupContainer = (): JSX.Element => {
  const navigate = useNavigate()
  const notification = useNotification()
  const { logEvent } = useAnalytics()

  useRedirectLoggedUser()
  useInitReCaptcha()

  const hookForm = useForm<ProUserCreationBodyV2Model>({
    defaultValues: SIGNUP_FORM_DEFAULT_VALUES,
    resolver: yupResolver(validationSchema),
    mode: 'onTouched',
  })

  const {
    handleSubmit,
    formState: { errors, touchedFields },
    setError,
    getValues,
  } = hookForm

  const onSubmit = async (values: ProUserCreationBodyV2Model) => {
    try {
      /* istanbul ignore next : ENV dependant */
      const token = await getReCaptchaToken('signup')
      await api.signupPro({
        ...values,
        token, // set token at form submission
      })
      onHandleSuccess()
    } catch (response) {
      if (response === RECAPTCHA_ERROR) {
        notification.error(RECAPTCHA_ERROR_MESSAGE)
      } else {
        const body = isErrorAPIError(response) ? response.body : {}
        onHandleFail(body)
      }
    }
  }

  const onHandleSuccess = () => {
    logEvent(Events.SIGNUP_FORM_SUCCESS, {})
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    navigate('/inscription/compte/confirmation', {
      replace: true,
      state: { email: getValues('email') },
    })
  }

  const onHandleFail = (errors: Partial<ProUserCreationBodyV2Model>) => {
    for (const [field, message] of Object.entries(errors)) {
      setError(field as keyof ProUserCreationBodyV2Model, {
        type: 'manual',
        message: message as string,
      })
    }

    notification.error(
      'Une ou plusieurs erreurs sont présentes dans le formulaire.'
    )
  }

  // Track the state of the form when the user gives up
  const touchedRef = useRef(touchedFields)
  const errorsRef = useRef(errors)

  useEffect(() => {
    touchedRef.current = touchedFields
    errorsRef.current = errors
  }, [touchedFields, errors])

  const logFormAbort = (): void | undefined => {
    const filledFields = Object.keys(touchedRef.current)
    if (filledFields.length === 0) {
      return
    }

    const filledWithErrors = Object.keys(
      Object.fromEntries(
        Object.entries(errorsRef.current).filter(([errorKey]) =>
          filledFields.includes(errorKey)
        )
      )
    )
    return logEvent(Events.SIGNUP_FORM_ABORT, {
      filled: filledFields,
      filledWithErrors: filledWithErrors,
    })
  }

  // Track the form state on tab closing
  useLogEventOnUnload(() => logFormAbort())

  // Track the form state on component unmount
  useEffect(() => {
    return () => {
      if (Object.keys(errorsRef.current).length === 0) {
        return
      }
      logFormAbort()
    }
  }, [])

  return (
    <section className={styles['content']}>
      <OperatingProcedures />

      <div className={styles['mandatory']}>
        <MandatoryInfo areAllFieldsMandatory={true} />
      </div>
      <FormProvider {...hookForm}>
        <form onSubmit={handleSubmit(onSubmit)}>
          <SignupForm />
        </form>
      </FormProvider>
    </section>
  )
}
