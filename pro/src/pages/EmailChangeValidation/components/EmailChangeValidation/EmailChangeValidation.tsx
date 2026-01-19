import { Button } from '@/design-system/Button/Button'

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
        <>
          <p className={styles['subtitle']}>
            Merci d’avoir confirmé votre changement d’adresse email.
          </p>
          <Button as="a" to="/" label="Se connecter" />
        </>
      )}
      {!isSuccess && (
        <>
          <p className={styles['subtitle']}>
            Votre adresse email n’a pas été modifiée car le lien reçu par mail
            expire 24 heures après sa réception.
          </p>
          <p className={styles['subtitle']}>
            Connectez-vous avec votre ancienne adresse email.
          </p>
          <Button as="a" to="/" label="Se connecter" />
        </>
      )}
    </>
  )
}
