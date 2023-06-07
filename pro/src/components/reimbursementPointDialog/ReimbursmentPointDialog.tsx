import React from 'react'

import { ExternalLinkIcon } from 'icons'
import { Button } from 'ui-kit/Button'
import CopyLink from 'ui-kit/CopyLink'
import { REACT_APP_DEMARCHES_SIMPLIFIEES_RIB_VENUE_PROCEDURE_ID_V4 } from 'utils/config'

import DialogBox from '../DialogBox'

import styles from './ReimbursmentPointDialog.module.scss'

interface ReimbursmentPointDialog {
  closeDialog: () => void
  dmsToken: string
}

const ReimbursmentPointDialog = ({
  closeDialog,
  dmsToken,
}: ReimbursmentPointDialog) => {
  const openDmsProcedure = () => {
    window.open(
      REACT_APP_DEMARCHES_SIMPLIFIEES_RIB_VENUE_PROCEDURE_ID_V4,
      '_blank'
    )
  }
  return (
    <DialogBox
      hasCloseButton={true}
      onDismiss={closeDialog}
      labelledBy={'confirmation coordonnées bancaires'}
      extraClassNames={styles['dialog-box']}
    >
      <div>
        <h3 className={styles['title']}>
          Avant d’ajouter des nouvelles coordonnées bancaires via la plateforme
          Démarches Simplifiées :
        </h3>
        <h4 className={styles['subtitle']}>Étape 1 : </h4>
        <p className={styles['description']}>
          Copiez l’identifiant ci-dessous qui vous permettra d’identifier votre
          lieu sur Démarches Simplifiées.
        </p>
        <CopyLink textToCopy={dmsToken} />
      </div>
      <hr className={styles['separator']} />
      <div>
        <h4 className={styles['subtitle']}>Étape 2 : </h4>
        <p className={styles['description']}>
          Cliquez sur le bouton “Continuer sur Démarches Simplifiées”. <br />
          Vous allez être redirigé sur la plateforme Démarches Simplifiées.
        </p>
        <Button
          className={styles['link-button']}
          onClick={openDmsProcedure}
          Icon={ExternalLinkIcon}
        >
          Continuer sur Démarches Simplifées
        </Button>
      </div>
    </DialogBox>
  )
}

export default ReimbursmentPointDialog
