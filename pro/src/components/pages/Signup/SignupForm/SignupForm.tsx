import * as pcapi from 'repository/pcapi/pcapi'

import { Button, SubmitButton, TextInput } from 'ui-kit'
import { Form, FormikProvider, useFormik } from 'formik'
import { ISignupApiErrorResponse, ISignupFormValues } from './types'
import { PasswordInput, SirenInput } from 'ui-kit/form'
import React, { useEffect } from 'react'
import { useHistory, useLocation } from 'react-router-dom'

import { BannerRGS } from 'new_components/Banner'
import { ButtonVariant } from 'ui-kit/Button/types'
import { Checkbox } from 'ui-kit'
import FormLayout from 'new_components/FormLayout'
import LegalInfos from 'components/layout/LegalInfos/LegalInfos'
import OperatingProcedures from './OperationProcedures'
import { SIGNUP_FORM_DEFAULT_VALUES } from './constants'
import { getSirenDataAdapter } from 'core/Offerers/adapters'
import { redirectLoggedUser } from 'components/router/helpers'
import { removeWhitespaces } from 'utils/string'
import useCurrentUser from 'components/hooks/useCurrentUser'
import useNotification from 'components/hooks/useNotification'
import { validationSchema } from './validationSchema'

const SignupForm = (): JSX.Element => {
  const history = useHistory()
  const notification = useNotification()
  const { currentUser } = useCurrentUser()
  const location = useLocation()

  useEffect(() => {
    console.log('useEffectRedirection')
    redirectLoggedUser(history, location, currentUser)
  }, [currentUser])

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
    pcapi
      .signup({
        ...flattenvalues,
        ...legalUnitValues,
        siren: removeWhitespaces(siren),
        publicName: firstName,
      })
      .then(() => onHandleSuccess())
      .catch(response => onHandleFail(response.errors ? response.errors : {}))
  }

  const onHandleSuccess = () => {
    history.replace('/inscription/confirmation')
  }

  const onHandleFail = (errors: ISignupApiErrorResponse) => {
    for (const field in errors)
      formik.setFieldError(field, (errors as any)[field])

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

  const getSirenAPIData = async (siren: string) => {
    const response = await getSirenDataAdapter(siren)
    if (response.isOk)
      formik.setFieldValue('legalUnitValues', response.payload.values)
    else formik.setFieldError('siren', response.message)
  }

  return (
    <section className="sign-up-form-page">
      <div className="content">
        <h1>Créer votre compte professionnel</h1>
        <h2>Merci de compléter les champs suivants pour créer votre compte.</h2>
        <OperatingProcedures />

        <div className="sign-up-tips">
          Tous les champs sont obligatoires sauf mention contraire
        </div>
        <FormikProvider value={formik}>
          <Form onSubmit={formik.handleSubmit}>
            <FormLayout>
              <div className="sign-up-form">
                <FormLayout.Row>
                  <TextInput
                    label="Adresse e-mail"
                    name="email"
                    placeholder="nom@exemple.fr"
                  />
                </FormLayout.Row>
                <FormLayout.Row>
                  <PasswordInput
                    name="password"
                    label="Mot de passe"
                    placeholder="Mon mot de passe"
                  />
                </FormLayout.Row>
                <FormLayout.Row>
                  <TextInput label="Nom" name="lastName" placeholder="Mon nom" />
                </FormLayout.Row>
                <FormLayout.Row>
                  <TextInput
                    label="Prénom"
                    name="firstName"
                    placeholder="Mon prénom"
                  />
                </FormLayout.Row>
                <FormLayout.Row>
                  <TextInput
                    label="Téléphone (utilisé uniquement par l’équipe du pass Culture)"
                    name="phoneNumber"
                    placeholder="Mon numéro de téléphone"
                  />
                </FormLayout.Row>
                <div className="siren-field">
                  <FormLayout.Row>
                    <SirenInput
                      label="SIREN de la structure que vous représentez"
                      onValidSiren={getSirenAPIData}
                    />
                  </FormLayout.Row>
                  <span className="field-siren-value">
                    {formik.values.legalUnitValues.name}
                  </span>
                </div>
                <FormLayout.Row>
                  <Checkbox
                    hideFooter
                    label="J’accepte d’être contacté par e-mail pour recevoir les
                      nouveautés du pass Culture et contribuer à son
                      amélioration (facultatif)"
                    name="contactOk"
                    value={formik.values.contactOk}
                  />
                </FormLayout.Row>
                <LegalInfos
                  className="sign-up-infos-before-signup"
                  title="Créer mon compte"
                />
                <BannerRGS />
              </div>
              <div className="buttons-field">
                <Button
                  onClick={() => history.push('/connexion')}
                  variant={ButtonVariant.SECONDARY}
                >
                  J’ai déjà un compte
                </Button>
                <SubmitButton
                  className="primary-button"
                  isLoading={formik.isSubmitting}
                  disabled={!formik.dirty || !formik.isValid}
                >
                  Créer mon compte
                </SubmitButton>
              </div>
            </FormLayout>
          </Form>
        </FormikProvider>
      </div>
    </section>
  )
}

export default SignupForm
