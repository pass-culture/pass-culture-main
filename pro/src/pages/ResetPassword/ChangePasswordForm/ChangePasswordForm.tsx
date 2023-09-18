import { Form, useFormikContext } from 'formik'
import React from 'react'

import FormLayout from 'components/FormLayout'
import { useScrollToFirstErrorAfterSubmit } from 'hooks'
import { PasswordInput, SubmitButton } from 'ui-kit'

import styles from './ChangePasswordForm.module.scss'

const ChangePasswordForm = (): JSX.Element => {
  const { handleSubmit, isSubmitting } = useFormikContext()
  useScrollToFirstErrorAfterSubmit()

  return (
    <Form onSubmit={handleSubmit} className={styles['change-password-form']}>
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
          isLoading={isSubmitting}
        >
          Valider
        </SubmitButton>
      </FormLayout>
    </Form>
  )
}

export default ChangePasswordForm
