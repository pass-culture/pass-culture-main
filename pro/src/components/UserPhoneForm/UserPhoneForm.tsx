import { Form, FormikProvider, useFormik } from 'formik'
import React from 'react'
import { useDispatch } from 'react-redux'

import { UserPhoneBodyModel } from 'apiClient/v1'
import { BoxFormLayout } from 'components/BoxFormLayout'
import FormLayout from 'components/FormLayout'
import { parseAndValidateFrenchPhoneNumber } from 'core/shared/utils/parseAndValidateFrenchPhoneNumber'
import useCurrentUser from 'hooks/useCurrentUser'
import { PatchPhoneAdapter } from 'pages/User/adapters/patchPhoneAdapter'
import { setCurrentUser } from 'store/user/actions'
import { TextInput, Button, SubmitButton } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './UserPhoneForm.module.scss'
import validationSchema from './validationSchema'

export interface UserPhoneFormProps {
  closeForm: () => void
  patchPhoneAdapter: PatchPhoneAdapter
  initialValues: UserPhoneBodyModel
}

const UserPhoneForm = ({
  closeForm,
  initialValues,
  patchPhoneAdapter,
}: UserPhoneFormProps): JSX.Element => {
  const { currentUser } = useCurrentUser()
  const dispatch = useDispatch()

  const onSubmit = (values: UserPhoneBodyModel) => {
    values.phoneNumber = parseAndValidateFrenchPhoneNumber(
      values.phoneNumber
    ).number
    patchPhoneAdapter(values).then(response => {
      if (response.isOk) {
        dispatch(
          setCurrentUser({
            ...currentUser,
            ...response.payload,
          })
        )
        closeForm()
      } else {
        for (const field in response.payload) {
          formik.setFieldError(field, response.payload[field])
        }
      }
    })
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
              <TextInput
                label="Téléphone"
                name="phoneNumber"
                placeholder="Votre téléphone"
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
  )
}

export default UserPhoneForm
