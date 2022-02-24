import PropTypes from 'prop-types'
import React, { useCallback, useRef } from 'react'

import DialogBox from 'new_components/DialogBox/DialogBox'
import * as pcapi from 'repository/pcapi/pcapi'

import { ReactComponent as DeletionIcon } from './assets/deletion.svg'

const DeleteStockDialog = ({
  isEvent,
  notifyDeletionError,
  notifyDeletionSuccess,
  onDelete,
  setIsDeleting,
  stockId,
}) => {
  const DIALOG_LABEL_ID = 'DIALOG_LABEL_ID'
  const deleteButtonRef = useRef()

  const confirmStockDeletion = useCallback(() => {
    pcapi
      .deleteStock(stockId)
      .then(() => {
        notifyDeletionSuccess()
        onDelete()
      })
      .catch(() => notifyDeletionError())
  }, [notifyDeletionError, notifyDeletionSuccess, onDelete, stockId])

  const abortStockDeletion = useCallback(
    () => setIsDeleting(false),
    [setIsDeleting]
  )

  return (
    <DialogBox
      extraClassNames="delete-stock-dialog"
      hasCloseButton={false}
      initialFocusRef={deleteButtonRef}
      labelledBy={DIALOG_LABEL_ID}
      onDismiss={abortStockDeletion}
    >
      <DeletionIcon />
      <h1 id={DIALOG_LABEL_ID}>Voulez-vous supprimer ce stock ?</h1>
      <p>
        {'Ce stock ne sera plus disponible à la réservation et '}
        <strong>
          entraînera l’annulation des réservations en cours
          {isEvent && ' et validées'} !
        </strong>
      </p>
      <p>
        L’ensemble des utilisateurs concernés sera automatiquement averti par
        e-mail.
      </p>
      <div className="action-buttons">
        <button
          className="secondary-button"
          onClick={abortStockDeletion}
          type="button"
        >
          Annuler
        </button>
        <button
          className="primary-button"
          onClick={confirmStockDeletion}
          ref={deleteButtonRef}
          type="button"
        >
          Supprimer
        </button>
      </div>
    </DialogBox>
  )
}

DeleteStockDialog.propTypes = {
  isEvent: PropTypes.bool.isRequired,
  notifyDeletionError: PropTypes.func.isRequired,
  notifyDeletionSuccess: PropTypes.func.isRequired,
  onDelete: PropTypes.func.isRequired,
  setIsDeleting: PropTypes.func.isRequired,
  stockId: PropTypes.string.isRequired,
}

export default DeleteStockDialog
