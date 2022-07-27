import React from 'react'
import { Form } from 'react-final-form'

import PasswordField from 'components/layout/form/fields/PasswordField'

import styles from './ChangePasswordForm.module.scss'

interface IChangePasswordForm {
  onSubmit: (values: Record<string, string>) => void
  newPasswordErrorMessage: string
  isChangePasswordSubmitDisabled: (values: Record<string, string>) => boolean
}

const ChangePasswordForm = ({
  isChangePasswordSubmitDisabled,
  newPasswordErrorMessage,
  onSubmit,
}: IChangePasswordForm): JSX.Element => (
  <section className={styles['change-password-form']}>
    <div className={styles['hero-body']}>
      <h1>Créer un nouveau mot de passe</h1>
      <p>Saisissez le nouveau mot de passe</p>
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
