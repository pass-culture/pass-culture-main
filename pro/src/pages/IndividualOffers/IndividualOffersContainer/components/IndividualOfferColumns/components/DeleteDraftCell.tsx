import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import fullTrashIcon from '@/icons/full-trash.svg'
import { DropdownItem } from '@/ui-kit/DropdownMenuWrapper/DropdownItem'

interface DeleteDraftOffersProps {
  setIsConfirmDialogOpen: (value: boolean) => void
}

export const DeleteDraftCell = ({
  setIsConfirmDialogOpen,
}: DeleteDraftOffersProps) => {
  return (
    <DropdownItem onSelect={() => setIsConfirmDialogOpen(true)}>
      <Button
        icon={fullTrashIcon}
        variant={ButtonVariant.TERTIARY}
        color={ButtonColor.NEUTRAL}
        label="Supprimer l’offre"
      />
    </DropdownItem>
  )
}
