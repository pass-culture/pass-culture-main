import { Form, FormikProvider, useFormik } from 'formik'
import React from 'react'

import FormLayout from 'new_components/FormLayout'
import { PasswordInput, SubmitButton } from 'ui-kit'

import styles from './ChangePasswordForm.module.scss'
import { validationSchema } from './validationSchema'
interface IChangePasswordForm {
  onSubmit: (values: Record<string, string>) => void
}

const ChangePasswordForm = ({ onSubmit }: IChangePasswordForm): JSX.Element => {
  const formik = useFormik({
    initialValues: { newPassword: '' },
    onSubmit: onSubmit,
    validationSchema: validationSchema,
  })
  return (
    <section className={styles['change-password-form']}>
      <div className={styles['hero-body']}>
        <h1>Créer un nouveau mot de passe</h1>
        <p>Saisissez le nouveau mot de passe</p>
        <FormikProvider value={formik}>
          <Form onSubmit={formik.handleSubmit}>
            <FormLayout>
              <FormLayout.Row>
                <PasswordInput
                  label="Nouveau mot de passe"
                  name="newPasswordValue"
                  placeholder="Mon nouveau mot de passe"
                />
              </FormLayout.Row>
              <SubmitButton isLoading={formik.isSubmitting}>
                Envoyer
              </SubmitButton>
            </FormLayout>
          </Form>
        </FormikProvider>
      </div>
    </section>
  )
}

export default ChangePasswordForm
