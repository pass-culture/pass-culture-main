import { ConfirmDialog } from '@/ui-kit/ConfirmDialog/ConfirmDialog'

interface ComplementaryInfosDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  openNextDialog: (open: boolean) => void
  onCancel?: () => void
}

export const ComplementaryInfosDialog = ({
  open,
  onOpenChange,
  openNextDialog,
  onCancel,
}: ComplementaryInfosDialogProps): JSX.Element => {
  return (
    <ConfirmDialog
      open={open}
      onConfirm={() => {
        onOpenChange(false)
        openNextDialog(true)
      }}
      onCancel={() => {
        onOpenChange(false)
        onCancel?.()
      }}
      title="Informations complémentaires requises"
      confirmText="Compléter maintenant"
      cancelText="Compléter plus tard"
    >
      Pour confirmer l'accueil du public, quelques précisions sont nécessaires.
      Vous pouvez les saisir directement dans le volet latéral.
    </ConfirmDialog>
  )
}
