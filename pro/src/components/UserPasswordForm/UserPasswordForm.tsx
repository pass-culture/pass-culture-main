import { Form, FormikProvider, useFormik } from 'formik'

import { api } from 'apiClient/api'
import { isErrorAPIError } from 'apiClient/helpers'
import { BoxFormLayout } from 'components/BoxFormLayout/BoxFormLayout'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { PasswordInput } from 'ui-kit/form/PasswordInput/PasswordInput'

import styles from './UserPasswordForm.module.scss'
import { validationSchema } from './validationSchema'

export interface UserPasswordFormProps {
  closeForm: () => void
}

type UserPasswordFormValues = {
  oldPassword: string
  newPassword: string
  newConfirmationPassword: string
}

export const UserPasswordForm = ({
  closeForm,
}: UserPasswordFormProps): JSX.Element => {
  const onSubmit = async (values: UserPasswordFormValues) => {
    try {
      await api.postChangePassword(values)
      closeForm()
    } catch (error) {
      if (isErrorAPIError(error)) {
        for (const field in error.body) {
          formik.setFieldError(field, error.body[field])
        }
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
              <Button type="submit" isLoading={formik.isSubmitting}>
                Enregistrer
              </Button>
            </div>
          </Form>
        </FormikProvider>
      </BoxFormLayout.Fields>
    </>
  )
}
