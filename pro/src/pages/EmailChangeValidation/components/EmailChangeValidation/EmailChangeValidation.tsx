import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './EmailChangeValidation.module.scss'

interface EmailChangeValidationProps {
  isSuccess: boolean
}

export const EmailChangeValidationScreen = ({
  isSuccess,
}: EmailChangeValidationProps): JSX.Element => {
  return (
    <>
      {isSuccess && (
        <section className={styles['content']}>
          <h1 className={styles['title']}>Et voilà !</h1>
          <p className={styles['subtitle']}>
            Merci d’avoir confirmé votre changement d’adresse email.
          </p>
          <ButtonLink variant={ButtonVariant.PRIMARY} to="/">
            Se connecter
          </ButtonLink>
        </section>
      )}
      {!isSuccess && (
        <section className={styles['content']}>
          <h1 className={styles['title']}>Votre lien a expiré !</h1>
          <p className={styles['subtitle']}>
            Votre adresse email n’a pas été modifiée car le lien reçu par mail
            expire 24 heures après sa réception.
          </p>
          <p className={styles['subtitle']}>
            Connectez-vous avec votre ancienne adresse email.
          </p>
          <ButtonLink variant={ButtonVariant.PRIMARY} to="/">
            Se connecter
          </ButtonLink>
        </section>
      )}
    </>
  )
}
