import { Form, FormikProvider, useFormik } from 'formik'
import React from 'react'

import { BoxFormLayout } from 'new_components/BoxFormLayout'
import FormLayout from 'new_components/FormLayout'
import { PostPasswordAdapter } from 'routes/User/adapters/postPasswordAdapter'
import { Button, SubmitButton, PasswordInput } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './UserPasswordForm.module.scss'
import validationSchema from './validationSchema'

export interface IUserPasswordFormProps {
  closeForm: () => void
  postPasswordAdapter: PostPasswordAdapter
}

const UserPasswordForm = ({
  closeForm,
  postPasswordAdapter,
}: IUserPasswordFormProps): JSX.Element => {
  const onSubmit = (values: any) => {
    postPasswordAdapter(values).then(response => {
      if (response.isOk) {
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
    <BoxFormLayout.Fields>
      <FormikProvider value={formik}>
        <Form onSubmit={formik.handleSubmit}>
          <FormLayout>
            <FormLayout.Row>
              <PasswordInput
                name="oldPassword"
                label="Mot de passe actuel"
                placeholder="Mon mot de passe actuel"
                renderTooltip={false}
              />
            </FormLayout.Row>
            <FormLayout.Row>
              <PasswordInput
                name="newPassword"
                label="Nouveau mot de passe"
                placeholder="Mon nouveau mot de pass"
                renderTooltip={false}
              />
            </FormLayout.Row>
            <FormLayout.Row>
              <PasswordInput
                name="newConfirmationPassword"
                label="Confirmer votre nouveau mot de passe"
                placeholder="Mon nouveau mot de pass"
                renderTooltip={false}
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
  )
}

export default UserPasswordForm
