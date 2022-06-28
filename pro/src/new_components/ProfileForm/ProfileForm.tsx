import { Button, SubmitButton } from 'ui-kit'
import { Form, FormikProvider, useFormik } from 'formik'
import React, { useState } from 'react'

import { AnySchema } from 'yup'
import { ButtonVariant } from 'ui-kit/Button/types'
import FormLayout from 'new_components/FormLayout'
import Icon from 'components/layout/Icon'
import styles from './ProfileForm.module.scss'

export interface IProfileFormProps {
  title: string
  subtitle: string
  fields: Array<JSX.Element>
  validationSchema: AnySchema
  banner?: JSX.Element
  shouldDisplayBanner: boolean
  onSubmit: (values: any) => void
  initialValues: { [id: string]: string }
}

const ProfileForm = ({
  title,
  subtitle,
  fields,
  validationSchema,
  initialValues,
  shouldDisplayBanner = false,
  banner,
  onSubmit,
}: IProfileFormProps): JSX.Element => {
  const [isFormVisible, setIsFormVisible] = useState(false)
  const toggleFormVisible = () => {
    setIsFormVisible(oldValue => !oldValue)
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
            {subtitle}
          </div>
        </div>
        <div className={styles['profile-form-description-column']}>
          {!isFormVisible && (
            <Button
              variant={ButtonVariant.TERNARY}
              onClick={toggleFormVisible}
              Icon={() => <Icon svg="ico-outer-pen" />}
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
              <FormLayout>
                {fields.map((item, index) => (
                  <FormLayout.Row key={index}>{item}</FormLayout.Row>
                ))}
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
                  disabled={!formik.dirty || !formik.isValid}
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
