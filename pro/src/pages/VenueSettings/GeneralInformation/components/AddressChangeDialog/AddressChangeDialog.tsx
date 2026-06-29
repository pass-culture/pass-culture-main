import { ConfirmDialog } from '@/ui-kit/ConfirmDialog/ConfirmDialog'

interface AddressChangeDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export const AddressChangeDialog = ({
  open,
  onOpenChange,
}: AddressChangeDialogProps): JSX.Element => {
  return (
    <ConfirmDialog
      open={open}
      onConfirm={() => onOpenChange(false)}
      onCancel={() => onOpenChange(false)}
      title="Important : Le changement d'adresse postale de votre structure ne
                    modifie pas automatiquement la localisation de vos offres existantes"
      overrideCancel
      confirmText="J'ai compris"
    >
      <span>
        Pour mettre à jour leur localisation, vous devrez les modifier une par
        une.
      </span>
    </ConfirmDialog>
  )
}
