import { Form, FormikProvider, useFormik } from 'formik'
import React, { useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'

import { api } from 'apiClient/api'
import { ProUserCreationBodyV2Model } from 'apiClient/v1'
import useAnalytics from 'app/App/analytics/firebase'
import { MandatoryInfo } from 'components/FormLayout/FormLayoutMandatoryInfo'
import { Events } from 'core/FirebaseEvents/constants'
import { useInitReCaptcha } from 'hooks/useInitReCaptcha'
import { useLogEventOnUnload } from 'hooks/useLogEventOnUnload'
import useNotification from 'hooks/useNotification'
import { useRedirectLoggedUser } from 'hooks/useRedirectLoggedUser'
import { getReCaptchaToken } from 'utils/recaptcha'

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

  const onSubmit = async (values: ProUserCreationBodyV2Model) => {
    /* istanbul ignore next : ENV dependant */
    values.token = await getReCaptchaToken('signup')

    try {
      await api.signupProV2({ ...values })
      onHandleSuccess()
    } catch (response) {
      // TODO type this
      // @ts-expect-error
      onHandleFail(response.body ? response.body : {})
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
    validationSchema,
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
      <h1>Créer votre compte</h1>
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
