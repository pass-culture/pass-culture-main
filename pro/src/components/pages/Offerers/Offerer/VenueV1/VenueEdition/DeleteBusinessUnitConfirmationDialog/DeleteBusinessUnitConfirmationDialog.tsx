import React from 'react'

import ConfirmDialog from 'new_components/ConfirmDialog'

interface IDeleteBusinessUnitConfirmationDialogProps {
  onConfirm: () => void
  onCancel: () => void
}

const DeleteBusinessUnitConfirmationDialog = ({
  onCancel,
  onConfirm,
}: IDeleteBusinessUnitConfirmationDialogProps): JSX.Element => {
  return (
    <ConfirmDialog
      cancelText="Annuler"
      confirmText="Continuer"
      onCancel={onCancel}
      onConfirm={onConfirm}
      title="Vous allez modifier les coordonnées bancaires associées à ce lieu"
    >
      <p>
        En modifiant ces coordonnées, vous les supprimez des autres lieux
        auxquels elles sont associées. Vous devrez associer à nouveau des
        coordonnées à ces lieux pour percevoir vos remboursements.
      </p>
      <br />
      <p>Souhaitez-vous continuer ?</p>
    </ConfirmDialog>
  )
}

export default DeleteBusinessUnitConfirmationDialog
