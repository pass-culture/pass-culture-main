import { Form, FormikProvider, useFormik } from 'formik'
import React, { useState } from 'react'
import { useDispatch } from 'react-redux'

import useCurrentUser from 'components/hooks/useCurrentUser'
import Icon from 'components/layout/Icon'
import FormLayout from 'new_components/FormLayout'
import { PatchIdentityAdapter } from 'routes/User/adapters/patchIdentityAdapter'
import { setCurrentUser } from 'store/user/actions'
import { TextInput, Button, SubmitButton } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import { IUserIdentityFormValues } from './types'
import styles from './UserIdentityForm.module.scss'
import validationSchema from './validationSchema'

export interface IUserIdentityFormProps {
  title: string
  subtitleFormat: (values: any) => string
  banner?: JSX.Element
  shouldDisplayBanner?: boolean
  patchIdentityAdapter: PatchIdentityAdapter
  initialValues: IUserIdentityFormValues
}

const UserIdentityForm = ({
  title,
  subtitleFormat,
  initialValues,
  shouldDisplayBanner = false,
  banner,
  patchIdentityAdapter,
}: IUserIdentityFormProps): JSX.Element => {
  const { currentUser } = useCurrentUser()
  const dispatch = useDispatch()
  const [isFormVisible, setIsFormVisible] = useState(false)
  const [subTitle, setSubTitle] = useState(subtitleFormat(initialValues))

  const onSubmit = (values: any) => {
    patchIdentityAdapter(values).then(response => {
      if (response.isOk) {
        formik.setValues(response.payload)
        setSubTitle(subtitleFormat(response.payload))
        dispatch(
          setCurrentUser({
            ...currentUser,
            ...response.payload,
          })
        )

        setIsFormVisible(false)
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
    setIsFormVisible(false)
  }

  const renderDetails = () => (
    <>
      <div className={styles['profile-form-description']}>
        <div className={styles['profile-form-description-column']}>
          <div className={styles['profile-form-description-title']}>
            {title}
          </div>
          <div className={styles['profile-form-description-value']}>
            {subTitle}
          </div>
        </div>
        <div className={styles['profile-form-description-column']}>
          <Button
            className={styles['profile-form-edit-button']}
            variant={ButtonVariant.TERNARY}
            onClick={() => setIsFormVisible(true)}
            Icon={() => <Icon svg="ico-pen-black" />}
          >
            Modifier
          </Button>
        </div>
      </div>
      {shouldDisplayBanner && (
        <div className={styles['profile-form-description-banner']}>
          {banner}
        </div>
      )}
    </>
  )

  const renderForm = () => (
    <div className={styles['profile-form-content']}>
      <FormikProvider value={formik}>
        <Form onSubmit={formik.handleSubmit}>
          <FormLayout className={styles['profile-form-field']}>
            <FormLayout.Row>
              <TextInput label="Prénom" name="firstName" />
            </FormLayout.Row>
            <FormLayout.Row>
              <TextInput label="Nom" name="lastName" />
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
    </div>
  )

  return (
    <div className={styles['profile-form']} data-testid="test-profile-form">
      {isFormVisible ? renderForm() : renderDetails()}
    </div>
  )
}

export default UserIdentityForm
