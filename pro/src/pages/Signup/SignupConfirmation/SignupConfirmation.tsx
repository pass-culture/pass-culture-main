import React from 'react'

import fullMailIcon from 'icons/full-mail.svg'
import { Banner, ButtonLink } from 'ui-kit'

import styles from './SignupConfirmation.module.scss'

const SignupConfirmation = () => (
  <section className={styles['content']}>
    <div className={styles['hero-body']}>
      <h1>Merci !</h1>
      <div className={styles['confirmation-text']}>
        Votre compte est en cours de création.
      </div>
      <div className={styles['confirmation-text']}>
        Vous allez recevoir un lien de confirmation par email. Cliquez sur ce
        lien pour confirmer la création de votre compte.
      </div>
      <Banner type="notification-info">
        <p>
          Si vous ne recevez pas d'email de notre part d'ici 5 minutes, vérifiez
          que le message n'est pas dans le dossier “indésirables” ou “spam” de
          votre messagerie.
        </p>
        <p className={styles['banner-text-gap']}>
          Si vous n’avez rien reçu d’ici demain, merci de contacter le support.
        </p>
        <ButtonLink
          link={{
            to: 'mailto:support-pro@passculture.app',
            isExternal: true,
            target: '_blank',
            rel: 'noopener noreferrer',
          }}
          icon={fullMailIcon}
          className={styles['contact-link']}
        >
          Contacter le support par mail à support-pro@passculture.app
        </ButtonLink>
      </Banner>
    </div>
  </section>
)

export default SignupConfirmation
