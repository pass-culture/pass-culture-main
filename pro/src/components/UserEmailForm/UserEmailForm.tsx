import { Form, FormikProvider, useFormik } from 'formik'
import React from 'react'

import { BoxFormLayout } from 'components/BoxFormLayout'
import FormLayout from 'components/FormLayout'
import useCurrentUser from 'hooks/useCurrentUser'
import { PostEmailAdapter } from 'pages/User/adapters/postEmailAdapter'
import { TextInput, Button, SubmitButton, PasswordInput } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './UserEmailForm.module.scss'
import validationSchema from './validationSchema'

export interface UserEmailFormProps {
  closeForm: () => void
  postEmailAdapter: PostEmailAdapter
  getPendingEmailRequest: () => void
}

type UserEmailFormValues = {
  email: string
  password: string
}

const UserEmailForm = ({
  closeForm,
  postEmailAdapter,
  getPendingEmailRequest,
}: UserEmailFormProps): JSX.Element => {
  const { currentUser } = useCurrentUser()
  const onSubmit = async (values: UserEmailFormValues) => {
    const response = await postEmailAdapter(values)
    if (response.isOk) {
      getPendingEmailRequest()
      closeForm()
    } else {
      for (const field in response.payload) {
        formik.setFieldError(field, response.payload[field])
      }
    }
    formik.setSubmitting(false)
  }

  const initialValues: UserEmailFormValues = {
    email: '',
    password: '',
  }

  const formik = useFormik({
    initialValues,
    onSubmit,
    validationSchema,
    validateOnChange: false,
  })

  const onCancel = () => {
    formik.resetForm()
    closeForm()
  }

  return (
    <>
      <BoxFormLayout.RequiredMessage />
      <BoxFormLayout.FormHeader
        textSecondary="Adresse email actuelle"
        textPrimary={currentUser.email}
      />
      <BoxFormLayout.Fields>
        <FormikProvider value={formik}>
          <Form onSubmit={formik.handleSubmit}>
            <FormLayout>
              <FormLayout.Row>
                <TextInput
                  label="Nouvelle adresse email"
                  name="email"
                  placeholder="email@exemple.com"
                />
              </FormLayout.Row>
              <FormLayout.Row>
                <PasswordInput
                  name="password"
                  label="Mot de passe (requis pour modifier votre email)"
                />
              </FormLayout.Row>
            </FormLayout>

            <div className={styles['buttons-field']}>
              <Button onClick={onCancel} variant={ButtonVariant.SECONDARY}>
                Annuler
              </Button>
              <SubmitButton isLoading={formik.isSubmitting}>
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
