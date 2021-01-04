import PropTypes from 'prop-types'
import React, { useCallback, useRef } from 'react'

import { DialogBox } from 'components/layout/DialogBox/DialogBox'
import * as pcapi from 'repository/pcapi/pcapi'

import { ReactComponent as DeletionIcon } from './assets/deletion.svg'

const DeleteStockDialog = ({
  notifyDeletionError,
  notifyDeletionSuccess,
  refreshOffer,
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
        refreshOffer()
      })
      .catch(() => notifyDeletionError())
  }, [notifyDeletionError, notifyDeletionSuccess, refreshOffer, stockId])

  const abortStockDeletion = useCallback(() => setIsDeleting(false), [setIsDeleting])

  return (
    <DialogBox
      extraClassNames="delete-stock-dialog"
      labelledBy={DIALOG_LABEL_ID}
      onDismiss={abortStockDeletion}
      ref={deleteButtonRef}
    >
      <DeletionIcon />
      <h1 id={DIALOG_LABEL_ID}>
        {'Voulez-vous supprimer ce stock ?'}
      </h1>
      <div>
        {'Ce stock ne sera plus disponible à la réservation et '}
        <strong>
          {'entraînera l’annulation des réservations en cours !'}
        </strong>
      </div>
      <div>
        {'L’ensemble des utilisateurs concernés sera automatiquement averti par e-mail.'}
      </div>
      <div className="action-buttons">
        <button
          className="secondary-button"
          onClick={abortStockDeletion}
          type="button"
        >
          {'Annuler'}
        </button>
        <button
          className="primary-button"
          onClick={confirmStockDeletion}
          ref={deleteButtonRef}
          type="button"
        >
          {'Supprimer'}
        </button>
      </div>
    </DialogBox>
  )
}

DeleteStockDialog.propTypes = {
  notifyDeletionError: PropTypes.func.isRequired,
  notifyDeletionSuccess: PropTypes.func.isRequired,
  refreshOffer: PropTypes.func.isRequired,
  setIsDeleting: PropTypes.func.isRequired,
  stockId: PropTypes.string.isRequired,
}

export default DeleteStockDialog
