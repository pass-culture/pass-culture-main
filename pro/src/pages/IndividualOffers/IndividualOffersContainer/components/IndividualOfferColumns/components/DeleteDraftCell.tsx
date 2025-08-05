import fullTrashIcon from 'icons/full-trash.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { DropdownItem } from 'ui-kit/DropdownMenuWrapper/DropdownItem'

interface DeleteDraftOffersProps {
  setIsConfirmDialogOpen: (value: boolean) => void
}

export const DeleteDraftCell = ({
  setIsConfirmDialogOpen,
}: DeleteDraftOffersProps) => {
  return (
    <DropdownItem onSelect={() => setIsConfirmDialogOpen(true)} asChild>
      <Button icon={fullTrashIcon} variant={ButtonVariant.TERNARY}>
        Supprimer l’offre
      </Button>
    </DropdownItem>
  )
}
