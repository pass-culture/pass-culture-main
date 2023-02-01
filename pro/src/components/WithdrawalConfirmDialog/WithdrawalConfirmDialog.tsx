import React from 'react'

import ConfirmDialog from 'components/Dialog/ConfirmDialog'
import { IcoMailOutline } from 'icons'

interface IWithdrawalConfirmDialogProps {
  saveDraft?: boolean
  handleConfirm: ({
    saveDraft,
    shouldSendMail,
  }?: {
    saveDraft?: boolean | undefined
    shouldSendMail?: boolean | undefined
  }) => void
}

const WithdrawalConfirmDialog = ({
  saveDraft = false,
  handleConfirm,
}: IWithdrawalConfirmDialogProps): JSX.Element => {
  return (
    <ConfirmDialog
      cancelText={'Ne pas envoyer'}
      confirmText={'Envoyer un e-mail'}
      onCancel={() => {
        handleConfirm({ saveDraft, shouldSendMail: false })
      }}
      onConfirm={() => {
        handleConfirm({ saveDraft, shouldSendMail: true })
      }}
      icon={IcoMailOutline}
      title="Souhaitez-vous prévenir les bénéficiaires de la modification des modalités de retrait ?"
    ></ConfirmDialog>
  )
}

export default WithdrawalConfirmDialog
