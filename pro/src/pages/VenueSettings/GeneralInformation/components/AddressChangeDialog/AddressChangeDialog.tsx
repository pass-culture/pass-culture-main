import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { SimpleModal } from '@/design-system/SimpleModal/SimpleModal'

interface AddressChangeDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export const AddressChangeDialog = ({
  open,
  onOpenChange,
}: AddressChangeDialogProps): JSX.Element => {
  return (
    <SimpleModal
      title="Important : Le changement d'adresse postale de votre structure ne
      modifie pas automatiquement la localisation de vos offres existantes"
      isOpen={open}
      onClose={() => onOpenChange(false)}
      actionButtons={[
        <Button
          onClick={() => onOpenChange(false)}
          key="confirm"
          variant={ButtonVariant.PRIMARY}
          color={ButtonColor.BRAND}
          label={"J'ai compris"}
        />,
      ]}
    >
      Pour mettre à jour leur localisation, vous devrez les modifier une par
      une.
    </SimpleModal>
  )
}
