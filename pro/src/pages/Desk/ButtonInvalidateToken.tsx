import React, { useState } from 'react'

import { ConfirmDialog } from '@/components/ConfirmDialog/ConfirmDialog'
import { Button } from '@/ui-kit/Button/Button'

interface ButtonInvalidateTokenProps {
  onConfirm: () => void
}

export const ButtonInvalidateToken = ({
  onConfirm,
}: ButtonInvalidateTokenProps): JSX.Element => {
  const [isDialogOpen, setIsDialogOpen] = useState(false)

  const openDialog = (event: React.MouseEvent<HTMLButtonElement>) => {
    event.preventDefault()
    setIsDialogOpen(true)
  }
  const closeDialog = () => {
    setIsDialogOpen(false)
  }
  const handleOnConfirm = () => {
    onConfirm()
    closeDialog()
  }

  return (
    <>
      <ConfirmDialog
        cancelText="Annuler"
        confirmText="Continuer"
        onCancel={closeDialog}
        onConfirm={handleOnConfirm}
        title="Voulez-vous vraiment invalider cette contremarque ?"
        open={isDialogOpen}
        trigger={
          <Button onClick={openDialog}>Invalider la contremarque</Button>
        }
      >
        <p>
          Cette contremarque a déjà été validée. Si vous l’invalidez, la
          réservation ne vous sera pas remboursée.
        </p>
      </ConfirmDialog>
    </>
  )
}
