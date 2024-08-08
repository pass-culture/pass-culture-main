import { Form, useField } from 'formik'
import React from 'react'

import { FormLayout } from 'components/FormLayout/FormLayout'
import { ScrollToFirstErrorAfterSubmit } from 'components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { EmailSpellCheckInput } from 'ui-kit/form/EmailSpellCheckInput/EmailSpellCheckInput'

import styles from './ChangePasswordRequestForm.module.scss'

export const ChangePasswordRequestForm = (): JSX.Element => {
  const [field] = useField('email')

  return (
    <section className={styles['change-password-request-form']}>
      <h1 className={styles['title']}>Mot de passe oublié ?</h1>
      <p className={styles['subtitle']}>
        Indiquez ci-dessous l’adresse email avec laquelle vous avez créé votre
        compte.
      </p>
      <Form>
        <ScrollToFirstErrorAfterSubmit />
        <FormLayout>
          <FormLayout.Row>
            <EmailSpellCheckInput
              name="email"
              description="Format : email@exemple.com"
              label="Adresse email"
            />
          </FormLayout.Row>
          <FormLayout.Row>
            <Button
              type="submit"
              className={styles['validation-button']}
              disabled={field.value === ''}
              variant={ButtonVariant.PRIMARY}
            >
              Valider
            </Button>
          </FormLayout.Row>
        </FormLayout>
      </Form>
    </section>
  )
}
