import { Form, FormikProvider, useFormik } from 'formik'
import React from 'react'

import useCurrentUser from 'components/hooks/useCurrentUser'
import { BoxFormLayout } from 'new_components/BoxFormLayout'
import FormLayout from 'new_components/FormLayout'
import { PostEmailAdapter } from 'routes/User/adapters/postEmailAdapter'
import { TextInput, Button, SubmitButton } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './UserEmailForm.module.scss'
import validationSchema from './validationSchema'

export interface IUserEmailFormProps {
  closeForm: () => void
  postEmailAdapter: PostEmailAdapter
  getPendingEmailRequest: () => void
}

const UserEmailForm = ({
  closeForm,
  postEmailAdapter,
  getPendingEmailRequest,
}: IUserEmailFormProps): JSX.Element => {
  const { currentUser } = useCurrentUser()
  const onSubmit = (values: any) => {
    postEmailAdapter(values).then(response => {
      if (response.isOk) {
        getPendingEmailRequest()
        closeForm()
      } else {
        for (const field in response.payload)
          formik.setFieldError(field, response.payload[field])
      }
    })
    formik.setSubmitting(false)
  }

  const formik = useFormik({
    initialValues: {},
    onSubmit: onSubmit,
    validationSchema,
    validateOnChange: false,
  })

  const onCancel = () => {
    formik.resetForm()
    closeForm()
  }

  return (
    <>
      <BoxFormLayout.FormHeader
        textSecondary="Adresse e-mail actuelle"
        textPrimary={currentUser.email}
      />
      <BoxFormLayout.Fields>
        <FormikProvider value={formik}>
          <Form onSubmit={formik.handleSubmit}>
            <FormLayout>
              <FormLayout.Row>
                <TextInput
                  label="Nouvelle adresse e-mail"
                  name="email"
                  placeholder="email@exemple.com"
                />
              </FormLayout.Row>
              <FormLayout.Row>
                <TextInput
                  label="Mot de passe (requis pour modifier votre e-mail)"
                  name="password"
                  type="password"
                  placeholder="Votre mot de passe"
                />
              </FormLayout.Row>
            </FormLayout>

            <div className={styles['buttons-field']}>
              <Button onClick={onCancel} variant={ButtonVariant.SECONDARY}>
                Annuler
              </Button>
              <SubmitButton
                className="primary-button"
                isLoading={formik.isSubmitting}
              >
                Enregistrer
              </SubmitButton>
            </div>
          </Form>
        </FormikProvider>
      </BoxFormLayout.Fields>
    </>
  )
}

export default UserEmailForm
