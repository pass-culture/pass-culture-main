import PropTypes from 'prop-types'
import React from 'react'

import { DialogBox } from 'components/layout/DialogBox/DialogBox'

import { ReactComponent as AddActivationCodeIcon } from '../assets/add-activation-code-light.svg'

export const ACTIVATION_CODES_UPLOAD_ID = 'ACTIVATION_CODES_UPLOAD_ID'

const ActivationCodesUploadDialog = ({ closeDialog }) => {
  return (
    <DialogBox
      extraClassNames="activation-codes-upload"
      hasCloseButton
      labelledBy={ACTIVATION_CODES_UPLOAD_ID}
      onDismiss={closeDialog}
    >
      <section className="activation-codes-upload-section">
        <h4 className="activation-codes-upload-title">
          {'Ajouter des codes d’activation'}
        </h4>
        <AddActivationCodeIcon
          alt="Ajouter des codes d'activation"
          aria-hidden
          className="activation-codes-upload-icon"
        />
      </section>
      <div className="activation-codes-upload-description">
        <span>
          {
            'Pour les offres nécessitants une activation par code sur une plateforme extérieure, vous pouvez importer directement un fichier .csv.'
          }
        </span>
        <span>
          {
            'Le stock disponible sera automatiquement mis à jour. Les jeunes auront accès à ce code dans leur espace réservation.'
          }
        </span>
      </div>
      <div className="activation-codes-upload-button-section">
        <button
          className="primary-button activation-codes-upload-button"
          type="button"
        >
          {"Importer un fichier .csv depuis l'ordinateur"}
        </button>
        <div className="activation-codes-upload-button-caption">
          <span>
            {'Format supporté : CSV'}
          </span>
          <span>
            {'Le poids du fichier ne doit pas dépasser 1 Mo'}
          </span>
        </div>
      </div>
      <div className="activation-codes-upload-separator" />
    </DialogBox>
  )
}

ActivationCodesUploadDialog.propTypes = {
  closeDialog: PropTypes.func.isRequired,
}

export default ActivationCodesUploadDialog
