import { Button, SubmitButton } from 'ui-kit'
import { Form, FormikProvider, useFormik } from 'formik'
import React, { useState } from 'react'

import { AnySchema } from 'yup'
import { ButtonVariant } from 'ui-kit/Button/types'
import FormLayout from 'new_components/FormLayout'
import Icon from 'components/layout/Icon'
import { PatchIdentityAdapter } from 'routes/User/adapters/patchIdentityAdapter'
import { setCurrentUser } from 'store/user/actions'
import styles from './ProfileForm.module.scss'
import useCurrentUser from 'components/hooks/useCurrentUser'
import { useDispatch } from 'react-redux'

export interface IProfileFormProps {
  title: string
  subtitleFormat: (values: any) => string
  fields: Array<JSX.Element>
  validationSchema: AnySchema
  banner?: JSX.Element
  shouldDisplayBanner?: boolean
  adapter: PatchIdentityAdapter
  initialValues: { [id: string]: string }
}

const ProfileForm = ({
  title,
  subtitleFormat,
  fields,
  validationSchema,
  initialValues,
  shouldDisplayBanner = false,
  banner,
  adapter,
}: IProfileFormProps): JSX.Element => {
  const { currentUser } = useCurrentUser()
  const dispatch = useDispatch()
  const [isFormVisible, setIsFormVisible] = useState(false)
  const [subTitle, setSubTitle] = useState(subtitleFormat(initialValues))
  const toggleFormVisible = () => {
    setIsFormVisible(oldValue => !oldValue)
  }
  const onSubmit = (values: any) => {
    adapter(values).then(response => {
      if (response.isOk) {
        formik.setValues(response.payload)
        setSubTitle(subtitleFormat(response.payload))
        dispatch(
          setCurrentUser({
            ...currentUser,
            ...response.payload,
          })
        )

        toggleFormVisible()
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
  return (
    <div className={styles['profile-form']} data-testid="test-profile-form">
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
          {!isFormVisible && (
            <Button
              className={styles['profile-form-edit-button']}
              variant={ButtonVariant.TERNARY}
              onClick={toggleFormVisible}
              Icon={() => <Icon svg="ico-pen-black" />}
            >
              Modifier
            </Button>
          )}
        </div>
      </div>
      {!isFormVisible && shouldDisplayBanner && (
        <div className={styles['profile-form-description-banner']}>
          {banner}
        </div>
      )}
      {isFormVisible && (
        <div className={styles['profile-form-content']}>
          <FormikProvider value={formik}>
            <Form onSubmit={formik.handleSubmit}>
              <FormLayout className={styles['profile-form-field']}>
                {fields}
              </FormLayout>

              <div className={styles['buttons-field']}>
                <Button
                  onClick={toggleFormVisible}
                  variant={ButtonVariant.SECONDARY}
                >
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
      )}
    </div>
  )
}

export default ProfileForm
