import React from 'react'

import styles from './ActivationCodeFormDialog.module.scss'

export const ActivationCodesUploadInformationDescription = () => {
  return (
    <div className={styles['activation-codes-upload-description']}>
      <p>
        Pour les offres nécessitant une activation par code sur une plateforme
        extérieure, vous pouvez importer directement un fichier .csv.
        <br />
        <br />
        Le stock disponible sera automatiquement mis à jour. Les bénéficiaires
        auront accès à ce code dans leur espace réservation.
      </p>
    </div>
  )
}
