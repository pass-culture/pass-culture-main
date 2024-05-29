import { Form, useFormikContext } from 'formik'
import React from 'react'

import { FormLayout } from 'components/FormLayout/FormLayout'
import { ScrollToFirstErrorAfterSubmit } from 'components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import { Button } from 'ui-kit/Button/Button'
import { PasswordInput } from 'ui-kit/form/PasswordInput/PasswordInput'

import styles from './ChangePasswordForm.module.scss'

export const ChangePasswordForm = (): JSX.Element => {
  const { handleSubmit, isSubmitting } = useFormikContext()

  return (
    <Form onSubmit={handleSubmit} className={styles['change-password-form']}>
      <ScrollToFirstErrorAfterSubmit />

      <FormLayout>
        <FormLayout.Row>
          <PasswordInput
            label="Nouveau mot de passe"
            name="newPasswordValue"
            withErrorPreview
          />
        </FormLayout.Row>
        <Button
          type="submit"
          className={styles['validation-button']}
          isLoading={isSubmitting}
        >
          Valider
        </Button>
      </FormLayout>
    </Form>
  )
}
