import { Form, FormikProvider, useFormik } from 'formik'
import { useDispatch } from 'react-redux'

import { api } from 'apiClient/api'
import { isErrorAPIError } from 'apiClient/helpers'
import { UserPhoneBodyModel } from 'apiClient/v1'
import { parseAndValidateFrenchPhoneNumber } from 'commons/core/shared/utils/parseAndValidateFrenchPhoneNumber'
import { useCurrentUser } from 'commons/hooks/useCurrentUser'
import { updateUser } from 'commons/store/user/reducer'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { BoxFormLayout } from 'ui-kit/BoxFormLayout/BoxFormLayout'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'

import styles from './UserForm.module.scss'
import { validationSchema } from './validationSchema'

export interface UserPhoneFormProps {
  closeForm: () => void
  initialValues: UserPhoneBodyModel
}

export const UserPhoneForm = ({
  closeForm,
  initialValues,
}: UserPhoneFormProps): JSX.Element => {
  const { currentUser } = useCurrentUser()
  const dispatch = useDispatch()

  const onSubmit = async (values: UserPhoneBodyModel) => {
    values.phoneNumber = parseAndValidateFrenchPhoneNumber(
      values.phoneNumber
    ).number

    try {
      const response = await api.patchUserPhone(values)
      dispatch(
        updateUser({
          ...currentUser,
          ...response,
        })
      )
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

  const formik = useFormik({
    initialValues: initialValues,
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
              <TextInput label="Téléphone" name="phoneNumber" />
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
  )
}
