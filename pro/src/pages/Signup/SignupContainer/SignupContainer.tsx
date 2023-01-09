import { Form, FormikProvider, useFormik } from 'formik'
import React, { useEffect, useRef } from 'react'
import { useHistory } from 'react-router-dom'

import { api } from 'apiClient/api'
import { Events } from 'core/FirebaseEvents/constants'
import useAnalytics from 'hooks/useAnalytics'
import useLogEventOnUnload from 'hooks/useLogEventOnUnload'
import { useModal } from 'hooks/useModal'
import useNotification from 'hooks/useNotification'
import useRedirectLoggedUser from 'hooks/useRedirectLoggedUser'
import { removeWhitespaces } from 'utils/string'

import { SIGNUP_FORM_DEFAULT_VALUES } from './constants'
import MaybeAppUserDialog from './MaybeAppUserDialog'
import OperatingProcedures from './OperationProcedures'
import SignupForm from './SignupForm'
import { ISignupApiErrorResponse, ISignupFormValues } from './types'
import { validationSchema } from './validationSchema'

const SignupContainer = (): JSX.Element => {
  const history = useHistory()
  const notification = useNotification()
  const { visible, hideModal } = useModal()
  const { logEvent } = useAnalytics()
  useRedirectLoggedUser()

  useEffect(() => {
    const script = document.createElement('script')

    script.src = '//js.hs-scripts.com/5119289.js'
    script.async = true
    script.type = 'text/javascript'
    script.id = 'hs-script-loader'
    script.defer = true

    document.body.appendChild(script)
    return () => {
      const script = document.getElementById('hs-script-loader') as Node
      document.body.removeChild(script)
    }
  }, [])

  const onSubmit = (values: ISignupFormValues) => {
    const { legalUnitValues, ...flattenvalues } = values
    const { firstName, siren } = flattenvalues
    api
      .signupPro({
        ...flattenvalues,
        ...legalUnitValues,
        siren: removeWhitespaces(siren),
        publicName: firstName,
      })
      .then(() => onHandleSuccess())
      .catch(response => onHandleFail(response.errors ? response.errors : {}))
  }

  const onHandleSuccess = () => {
    logEvent?.(Events.SIGNUP_FORM_SUCCESS, {})
    history.replace('/inscription/confirmation')
  }

  const onHandleFail = (errors: ISignupApiErrorResponse) => {
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
    validateOnChange: false,
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
    return logEvent?.(Events.SIGNUP_FORM_ABORT, {
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
    <section className="sign-up-form-page">
      {visible && <MaybeAppUserDialog onCancel={hideModal} />}
      <div className="content">
        <h1>Créer votre compte professionnel</h1>
        <OperatingProcedures />

        <div className="sign-up-tips">
          Tous les champs sont obligatoires sauf mention contraire
        </div>
        <FormikProvider value={formik}>
          <Form onSubmit={formik.handleSubmit}>
            <SignupForm />
          </Form>
        </FormikProvider>
      </div>
    </section>
  )
}

export default SignupContainer
