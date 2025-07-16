import { useLocation } from 'react-router'

import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { useRedirectLoggedUser } from 'commons/hooks/useRedirectLoggedUser'
import { ReSendEmailCallout } from 'components/ReSendEmailCallout/ReSendEmailCallout'
import fullMailIcon from 'icons/full-mail.svg'
import { Callout } from 'ui-kit/Callout/Callout'

import styles from './SignupConfirmation.module.scss'

export const SignupConfirmation = () => {
  useRedirectLoggedUser()
  const isNewSignupEnabled = useActiveFeature('WIP_2025_SIGN_UP')
  const location = useLocation()

  return isNewSignupEnabled ? (
    <section className={styles['signup-confirmation']}>
      <h1 className={styles['signup-confirmation-title']}>
        Validez votre adresse email
      </h1>
      <p className={styles['signup-confirmation-body']}>
        Cliquez sur le lien envoyé par email
        {location.state?.email && (
          <>
            {' '}
            à <b>{location.state.email}</b>
          </>
        )}
      </p>
      <ReSendEmailCallout hideLink />
    </section>
  ) : (
    <section className={styles['content']}>
      <div className={styles['hero-body']}>
        <h1 className={styles['title']}>Validez votre adresse email</h1>
        <div className={styles['confirmation-text']}>
          Votre compte est en cours de création.
        </div>
        <div className={styles['confirmation-text']}>
          Vous allez recevoir un lien de confirmation par email. Cliquez sur ce
          lien pour confirmer la création de votre compte.
        </div>
        <Callout
          links={[
            {
              href: 'mailto:support-pro@passculture.app',
              isExternal: true,
              icon: { src: fullMailIcon, alt: 'Nouvelle fenêtre, par email' },
              label:
                'Contacter notre support par mail à support-pro@passculture.app',
            },
          ]}
        >
          <p>
            Si vous ne recevez pas d’email de notre part d’ici 5 minutes,
            vérifiez que le message n’est pas dans le dossier “indésirables” ou
            “spam” de votre messagerie.
          </p>
          <p className={styles['banner-text-gap']}>
            Si vous n’avez rien reçu d’ici demain, merci de contacter le
            support.
          </p>
        </Callout>
      </div>
    </section>
  )
}
