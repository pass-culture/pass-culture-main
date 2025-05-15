import { ConfirmDialog } from 'components/ConfirmDialog/ConfirmDialog'
import { Button } from 'ui-kit/Button/Button'

interface ButtonInvalidateTokenProps {
  onConfirm: () => void
}

export const ButtonInvalidateToken = ({
  onConfirm,
}: ButtonInvalidateTokenProps): JSX.Element => {
  return (
    <>
      <ConfirmDialog
        cancelText="Annuler"
        confirmText="Continuer"
        onCancel={() => {}}
        onConfirm={onConfirm}
        title="Voulez-vous vraiment invalider cette contremarque ?"
        trigger={<Button>Invalider la contremarque</Button>}
      >
        <p>
          Cette contremarque a déjà été validée. Si vous l’invalidez, la
          réservation ne vous sera pas remboursée.
        </p>
      </ConfirmDialog>
    </>
  )
}
