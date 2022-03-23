import React from 'react'
import { Form } from 'react-final-form'

import PasswordField from 'components/layout/form/fields/PasswordField'

import styles from './ChangePasswordForm.module.scss'

interface iChangePasswordForm {
  onSubmit: () => void
  newPasswordErrorMessage: string
  isChangePasswordSubmitDisabled: (values: Record<string, string>) => boolean
}

const ChangePasswordForm = ({
  isChangePasswordSubmitDisabled,
  newPasswordErrorMessage,
  onSubmit,
}: iChangePasswordForm): JSX.Element => (
  <section className={styles['change-password-form']}>
    <div className={styles['hero-body']}>
      <h1>Créer un nouveau mot de passe</h1>
      <h2>Saisissez le nouveau mot de passe</h2>
      <Form onSubmit={onSubmit}>
        {({ handleSubmit, errors, values }) => (
          <form onSubmit={handleSubmit}>
            <PasswordField
              errors={
                errors?.newPasswordValue
                  ? errors?.newPasswordValue
                  : newPasswordErrorMessage
                  ? [newPasswordErrorMessage]
                  : null
              }
              label="Nouveau mot de passe"
              name="newPasswordValue"
              placeholder="Mon nouveau mot de passe"
              showTooltip
            />
            <button
              className="primary-button submit-button"
              disabled={isChangePasswordSubmitDisabled(values)}
              type="submit"
            >
              Envoyer
            </button>
          </form>
        )}
      </Form>
    </div>
  </section>
)

export default ChangePasswordForm
