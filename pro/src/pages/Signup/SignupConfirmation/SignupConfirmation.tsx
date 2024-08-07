import React from 'react'

import { Callout } from 'components/Callout/Callout'
import fullMailIcon from 'icons/full-mail.svg'

import styles from './SignupConfirmation.module.scss'

export const SignupConfirmation = () => (
  <section className={styles['content']}>
    <div className={styles['hero-body']}>
      <h1 className={styles['title']}>Merci !</h1>
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
          Si vous ne recevez pas d’email de notre part d’ici 5 minutes, vérifiez
          que le message n’est pas dans le dossier “indésirables” ou “spam” de
          votre messagerie.
        </p>
        <p className={styles['banner-text-gap']}>
          Si vous n’avez rien reçu d’ici demain, merci de contacter le support.
        </p>
      </Callout>
    </div>
  </section>
)
