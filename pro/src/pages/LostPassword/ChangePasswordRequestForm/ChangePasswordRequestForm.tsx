import { Form, useField } from 'formik'
import React from 'react'

import FormLayout from 'components/FormLayout'
import { useScrollToFirstErrorAfterSubmit } from 'hooks'
import { SubmitButton } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import EmailSpellCheckInput from 'ui-kit/form/EmailSpellCheckInput'

import styles from './ChangePasswordRequestForm.module.scss'

const ChangePasswordRequestForm = (): JSX.Element => {
  useScrollToFirstErrorAfterSubmit()
  const [field] = useField('email')

  return (
    <section className={styles['change-password-request-form']}>
      <h1 className={styles['title']}>Mot de passe oublié ?</h1>
      <p className={styles['subtitle']}>
        Indiquez ci-dessous l’adresse email avec laquelle vous avez créé votre
        compte.
      </p>
      <Form>
        <FormLayout>
          <FormLayout.Row>
            <EmailSpellCheckInput
              name="email"
              placeholder="email@exemple.com"
              label="Adresse email"
            />
          </FormLayout.Row>
          <FormLayout.Row>
            <SubmitButton
              className={styles['validation-button']}
              disabled={field.value === ''}
              variant={ButtonVariant.PRIMARY}
            >
              Valider
            </SubmitButton>
          </FormLayout.Row>
        </FormLayout>
      </Form>
    </section>
  )
}

export default ChangePasswordRequestForm
