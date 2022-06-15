import { ReactComponent as InfoIcon } from './assets/info.svg'
import React from 'react'
import { Title } from 'ui-kit'
import styles from './LeavingOfferCreationDialog.module.scss'

const LeavingOfferCreationDialog = (): JSX.Element => {
  return (
    <div className={styles['dialog']}>
      <InfoIcon className={styles['dialog-icon']} />
      <Title level={3}>Voulez-vous quitter la création d’offre ?</Title>
      <p>
        Votre offre ne sera pas sauvegardée et toutes les informations seront
        perdues.
      </p>
    </div>
  )
}

export default LeavingOfferCreationDialog
