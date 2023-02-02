import React from 'react'

import ConfirmDialog from 'components/Dialog/ConfirmDialog'
import { IcoMailOutline } from 'icons'

interface IWithdrawalConfirmDialogProps {
  hideDialog: () => void
  handleCancel: () => void
  handleConfirm: () => void
}

const WithdrawalConfirmDialog = ({
  hideDialog,
  handleCancel,
  handleConfirm,
}: IWithdrawalConfirmDialogProps): JSX.Element => {
  return (
    <ConfirmDialog
      cancelText={'Ne pas envoyer'}
      confirmText={'Envoyer un e-mail'}
      leftButtonAction={handleCancel}
      onCancel={hideDialog}
      onConfirm={handleConfirm}
      icon={IcoMailOutline}
      title="Souhaitez-vous prévenir les bénéficiaires de la modification des modalités de retrait ?"
    ></ConfirmDialog>
  )
}

export default WithdrawalConfirmDialog
