import React from 'react'

import { DialogBox } from 'new_components/DialogBox'
import { Button } from 'ui-kit/Button'
import CopyLink from 'ui-kit/CopyLink'
import Icon from 'ui-kit/Icon/Icon'
import { REACT_APP_DEMARCHES_SIMPLIFIEES_RIB_VENUE_PROCEDURE_ID_V4 } from 'utils/config'

import styles from './ReimbursementPointDialog.module.scss'

export interface IReimbursementPointDialog {
  closeDialog: () => void
  dmsToken: string
}
const ReimbursementPointDialog = ({
  closeDialog,
  dmsToken,
}: IReimbursementPointDialog) => {
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
          Copiez le numéro d’identifiant de votre lieu qui vous permettra
          d’identifier votre lieu sur Démarches Simplifiées.
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
        <Button className={styles['link-button']} onClick={openDmsProcedure}>
          <Icon
            className={styles['icon-button']}
            svg="ico-fill-external-link"
          />
          Continuer sur Démarches Simplifées
        </Button>
      </div>
    </DialogBox>
  )
}

export default ReimbursementPointDialog
