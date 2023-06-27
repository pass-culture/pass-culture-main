import React, { useState } from 'react'

import ConfirmDialog from 'components/Dialog/ConfirmDialog'
import { Button } from 'ui-kit'

interface ButtonInvalidateTokenProps {
  onConfirm: () => void
}

const ButtonInvalidateToken = ({
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
      <Button onClick={openDialog}>Invalider la contremarque</Button>
      {isDialogOpen && (
        <ConfirmDialog
          cancelText="Annuler"
          confirmText="Continuer"
          onCancel={closeDialog}
          onConfirm={handleOnConfirm}
          title="Voulez-vous vraiment invalider cette contremarque ?"
        >
          <p>
            Cette contremarque a déjà été validée. Si vous l’invalidez, la
            réservation ne vous sera pas remboursée.
          </p>
        </ConfirmDialog>
      )}
    </>
  )
}

export default ButtonInvalidateToken
