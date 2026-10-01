import { useLocation } from 'react-router'

import { ReSendEmailCallout } from '@/components/ReSendEmailCallout/ReSendEmailCallout'

import styles from './SignupConfirmation.module.scss'

export const SignupConfirmation = () => {
  const location = useLocation()

  return (
    <section className={styles['signup-confirmation-container']}>
      <h1 className={styles['title']}>Validez votre adresse email</h1>
      <p className={styles['signup-confirmation']}>
        Cliquez sur le lien envoyé par email
        {location.state?.email && (
          <>
            {' '}
            à<br />
            <b>{location.state.email}</b>
          </>
        )}
      </p>
      <ReSendEmailCallout hideLink />
    </section>
  )
}
