import type React from 'react'
import { useState } from 'react'

import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { SimpleModal } from '@/design-system/SimpleModal/SimpleModal'

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
      <Button onClick={openDialog} label="Invalider la contremarque" />
      <SimpleModal
        title="Voulez-vous vraiment invalider cette contremarque ?"
        isOpen={isDialogOpen}
        onClose={closeDialog}
        actionButtons={[
          <Button
            onClick={closeDialog}
            variant={ButtonVariant.SECONDARY}
            color={ButtonColor.NEUTRAL}
            label="Annuler"
            key="cancel"
          />,
          <Button onClick={handleOnConfirm} label="Continuer" key="confirm" />,
        ]}
      >
        <p>
          Cette contremarque a déjà été validée. Si vous l'invalidez, la
          réservation ne vous sera pas remboursée.
        </p>
      </SimpleModal>
    </>
  )
}
