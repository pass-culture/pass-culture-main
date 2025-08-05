import { useRedirectLoggedUser } from 'commons/hooks/useRedirectLoggedUser'
import { ReSendEmailCallout } from 'components/ReSendEmailCallout/ReSendEmailCallout'
import { useLocation } from 'react-router'

import styles from './SignupConfirmation.module.scss'

export const SignupConfirmation = () => {
  useRedirectLoggedUser()
  const location = useLocation()

  return (
    <section className={styles['signup-confirmation']}>
      <p className={styles['signup-confirmation-body']}>
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
