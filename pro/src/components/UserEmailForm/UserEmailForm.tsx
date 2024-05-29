import { Form, FormikProvider, useFormik } from 'formik'

import { api } from 'apiClient/api'
import { isErrorAPIError } from 'apiClient/helpers'
import { UserResetEmailBodyModel } from 'apiClient/v1'
import { BoxFormLayout } from 'components/BoxFormLayout/BoxFormLayout'
import { FormLayout } from 'components/FormLayout/FormLayout'
import useCurrentUser from 'hooks/useCurrentUser'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { PasswordInput } from 'ui-kit/form/PasswordInput/PasswordInput'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'

import styles from './UserEmailForm.module.scss'
import { validationSchema } from './validationSchema'

export interface UserEmailFormProps {
  closeForm: () => void
  getPendingEmailRequest: () => void
}

type UserEmailFormValues = {
  email: string
  password: string
}

export const UserEmailForm = ({
  closeForm,
  getPendingEmailRequest,
}: UserEmailFormProps): JSX.Element => {
  const { currentUser } = useCurrentUser()

  const onSubmit = async (values: UserResetEmailBodyModel) => {
    try {
      await api.postUserEmail(values)

      getPendingEmailRequest()
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
