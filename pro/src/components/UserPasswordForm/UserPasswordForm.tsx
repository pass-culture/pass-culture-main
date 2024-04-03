import { Form, FormikProvider, useFormik } from 'formik'
import React from 'react'

import { BoxFormLayout } from 'components/BoxFormLayout'
import FormLayout from 'components/FormLayout'
import { PostPasswordAdapter } from 'pages/User/adapters/postPasswordAdapter'
import { Button, SubmitButton, PasswordInput } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './UserPasswordForm.module.scss'
import validationSchema from './validationSchema'

export interface UserPasswordFormProps {
  closeForm: () => void
  postPasswordAdapter: PostPasswordAdapter
}

type UserPasswordFormValues = {
  oldPassword: string
  newPassword: string
  newConfirmationPassword: string
}

const UserPasswordForm = ({
  closeForm,
  postPasswordAdapter,
}: UserPasswordFormProps): JSX.Element => {
  const onSubmit = async (values: UserPasswordFormValues) => {
    const response = await postPasswordAdapter(values)
    if (response.isOk) {
      closeForm()
    } else {
      for (const field in response.payload) {
        formik.setFieldError(field, response.payload[field])
      }
    }
    formik.setSubmitting(false)
  }

  const initialValues: UserPasswordFormValues = {
    oldPassword: '',
    newPassword: '',
    newConfirmationPassword: '',
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
      <BoxFormLayout.Fields>
        <FormikProvider value={formik}>
          <Form onSubmit={formik.handleSubmit}>
            <FormLayout>
              <FormLayout.Row>
                <PasswordInput name="oldPassword" label="Mot de passe actuel" />
              </FormLayout.Row>
              <FormLayout.Row>
                <PasswordInput
                  name="newPassword"
                  label="Nouveau mot de passe"
                  withErrorPreview={true}
                />
              </FormLayout.Row>
              <FormLayout.Row>
                <PasswordInput
                  name="newConfirmationPassword"
                  label="Confirmer votre nouveau mot de passe"
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

export default UserPasswordForm
