import { Form, FormikProvider, useFormik } from 'formik'
import React from 'react'

import FormLayout from 'components/FormLayout'
import { PasswordInput, SubmitButton } from 'ui-kit'

import styles from './ChangePasswordForm.module.scss'
import { validationSchema } from './validationSchema'
interface ChangePasswordFormProps {
  onSubmit: (values: Record<string, string>) => void
}

const ChangePasswordForm = ({
  onSubmit,
}: ChangePasswordFormProps): JSX.Element => {
  const formik = useFormik({
    initialValues: { newPasswordValue: '' },
    onSubmit: onSubmit,
    validationSchema: validationSchema,
  })
  return (
    <section className={styles['change-password-form']}>
      <h1>Définir un nouveau mot de passe</h1>
      <FormikProvider value={formik}>
        <Form onSubmit={formik.handleSubmit}>
          <FormLayout>
            <FormLayout.Row>
              <PasswordInput
                label="Nouveau mot de passe"
                name="newPasswordValue"
                withErrorPreview
              />
            </FormLayout.Row>
            <SubmitButton
              className={styles['validation-button']}
              isLoading={formik.isSubmitting}
            >
              Valider
            </SubmitButton>
          </FormLayout>
        </Form>
      </FormikProvider>
    </section>
  )
}

export default ChangePasswordForm
