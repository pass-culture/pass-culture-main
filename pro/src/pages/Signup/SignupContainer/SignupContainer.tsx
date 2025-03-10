import { Form, FormikProvider, useFormik } from 'formik'
import { useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'

import { api } from 'apiClient/api'
import { isErrorAPIError } from 'apiClient/helpers'
import { ProUserCreationBodyV2Model } from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import { Events } from 'commons/core/FirebaseEvents/constants'
import {
  RECAPTCHA_ERROR,
  RECAPTCHA_ERROR_MESSAGE,
} from 'commons/core/shared/constants'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { useInitReCaptcha } from 'commons/hooks/useInitReCaptcha'
import { useLogEventOnUnload } from 'commons/hooks/useLogEventOnUnload'
import { useNotification } from 'commons/hooks/useNotification'
import { useRedirectLoggedUser } from 'commons/hooks/useRedirectLoggedUser'
import { getReCaptchaToken } from 'commons/utils/recaptcha'
import { MandatoryInfo } from 'components/FormLayout/FormLayoutMandatoryInfo'

import { SIGNUP_FORM_DEFAULT_VALUES } from './constants'
import { OperatingProcedures } from './OperationProcedures/OperationProcedures'
import styles from './SignupContainer.module.scss'
import { SignupForm } from './SignupForm'
import { validationSchema } from './validationSchema'

export const SignupContainer = (): JSX.Element => {
  const navigate = useNavigate()
  const notification = useNotification()
  const { logEvent } = useAnalytics()
  const isNewSignupEnabled = useActiveFeature('WIP_2025_SIGN_UP')

  useRedirectLoggedUser()
  useInitReCaptcha()

  const onSubmit = async (values: ProUserCreationBodyV2Model) => {
    try {
      /* istanbul ignore next : ENV dependant */
      values.token = await getReCaptchaToken('signup')
      await api.signupPro({ ...values })
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
    navigate('/inscription/confirmation', { replace: true })
  }

  const onHandleFail = (errors: Partial<ProUserCreationBodyV2Model>) => {
    for (const field in errors) {
      formik.setFieldError(field, (errors as any)[field])
    }

    notification.error(
      'Une ou plusieurs erreurs sont présentes dans le formulaire.'
    )
    formik.setSubmitting(false)
  }

  const formik = useFormik({
    initialValues: SIGNUP_FORM_DEFAULT_VALUES,
    onSubmit: onSubmit,
    validationSchema: validationSchema(isNewSignupEnabled),
    validateOnChange: true,
  })

  // Track the state of the form when the user gives up
  const touchedRef = useRef(formik.touched)
  const errorsRef = useRef(formik.errors)

  useEffect(() => {
    touchedRef.current = formik.touched
    errorsRef.current = formik.errors
  }, [formik.touched, formik.errors])

  const logFormAbort = (): void | undefined => {
    const filledFields = Object.keys(touchedRef.current)
    if (filledFields.length === 0) {
      return
    }
    // formik.errors contains every fields with errors even if they have not been touched.
    // We filter theses errors by touched fields to only have fields filled by the user with errors
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
      if (Object.entries(errorsRef.current).length === 0) {
        return
      }
      logFormAbort()
    }
  }, [])

  return (
    <section className={styles['content']}>
      <h1 className={styles['title']}>Créer votre compte</h1>
      <OperatingProcedures />

      <div className={styles['mandatory']}>
        <MandatoryInfo />
      </div>
      <FormikProvider value={formik}>
        <Form onSubmit={formik.handleSubmit}>
          <SignupForm />
        </Form>
      </FormikProvider>
    </section>
  )
}
