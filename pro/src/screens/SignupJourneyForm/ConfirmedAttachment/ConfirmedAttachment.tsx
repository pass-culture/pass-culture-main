import React from 'react'

import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './ConfirmedAttachment.module.scss'

const ConfirmedAttachment = (): JSX.Element => {
  return (
    <div className={styles['confirmed-attachment-layout']}>
      <div className={styles['title']}>Votre demande a été prise en compte</div>
      <div className={styles['informations']}>
        Un e-mail vous sera envoyé lors de la validation de votre demande. Vous
        aurez alors accès à l’ensemble des fonctionnalités du pass Culture Pro.
      </div>
      <ButtonLink
        className={styles['home-button']}
        variant={ButtonVariant.PRIMARY}
        link={{ isExternal: false, to: '/' }}
      >
        Accéder à votre espace
      </ButtonLink>
    </div>
  )
}
export default ConfirmedAttachment
