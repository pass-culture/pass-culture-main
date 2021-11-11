/*
* @debt complexity "Gaël: file nested too deep in directory structure"
* @debt directory "Gaël: this file should be migrated within the new directory structure"
*/

import React from 'react'

const ActivationCodesUploadInformationDescription = () => {
  return (
    <div className="activation-codes-upload-description">
      <p>
        Pour les offres nécessitant une activation par code sur une plateforme extérieure, vous pouvez importer directement un fichier .csv.
      </p>
      <p>
        Le stock disponible sera automatiquement mis à jour. Les bénéficiaires auront accès à ce code dans leur espace réservation.
      </p>
    </div>
  )
}

export default ActivationCodesUploadInformationDescription
