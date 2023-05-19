import React from 'react'

import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './Welcome.module.scss'

const Welcome = (): JSX.Element => {
  return (
    <div className={styles['welcome-layout']}>
      <div className={styles['title']}>Finalisez votre inscription</div>
      <div className={styles['informations']}>
        Avant de commencer, munissez-vous du numéro de SIRET de votre structure.{' '}
      </div>
      <ButtonLink
        className={styles['continue-button']}
        variant={ButtonVariant.PRIMARY}
        link={{ isExternal: false, to: '/parcours-inscription/structure' }}
      >
        Commencer
      </ButtonLink>
      <div className={styles['caption-informations']}>
        <div>Vous préférez continuer plus tard ?</div>
        <div>Utilisez simplement vos identifiants pour vous reconnecter.</div>
      </div>
    </div>
  )
}
export default Welcome
