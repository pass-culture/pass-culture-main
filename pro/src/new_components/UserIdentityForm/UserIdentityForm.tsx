import { Form, FormikProvider, useFormik } from 'formik'
import React from 'react'
import { useDispatch } from 'react-redux'

import useCurrentUser from 'components/hooks/useCurrentUser'
import { BoxFormLayout } from 'new_components/BoxFormLayout'
import FormLayout from 'new_components/FormLayout'
import { PatchIdentityAdapter } from 'routes/User/adapters/patchIdentityAdapter'
import { setCurrentUser } from 'store/user/actions'
import { TextInput, Button, SubmitButton } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import { IUserIdentityFormValues } from './types'
import styles from './UserIdentityForm.module.scss'
import validationSchema from './validationSchema'

export interface IUserIdentityFormProps {
  closeForm: () => void
  patchIdentityAdapter: PatchIdentityAdapter
  initialValues: IUserIdentityFormValues
}

const UserIdentityForm = ({
  closeForm,
  initialValues,
  patchIdentityAdapter,
}: IUserIdentityFormProps): JSX.Element => {
  const { currentUser } = useCurrentUser()
  const dispatch = useDispatch()

  const onSubmit = (values: any) => {
    patchIdentityAdapter(values).then(response => {
      if (response.isOk) {
        dispatch(
          setCurrentUser({
            ...currentUser,
            ...response.payload,
          })
        )
        closeForm()
      } else {
        for (const field in response.payload)
          formik.setFieldError(field, response.payload[field])
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
    <>
      <BoxFormLayout.RequiredMessage />
      <BoxFormLayout.Fields>
        <FormikProvider value={formik}>
          <Form onSubmit={formik.handleSubmit}>
            <FormLayout>
              <FormLayout.Row>
                <TextInput
                  label="Prénom"
                  name="firstName"
                  placeholder="Votre prénom"
                />
              </FormLayout.Row>
              <FormLayout.Row>
                <TextInput
                  label="Nom"
                  name="lastName"
                  placeholder="Votre nom"
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

export default UserIdentityForm
