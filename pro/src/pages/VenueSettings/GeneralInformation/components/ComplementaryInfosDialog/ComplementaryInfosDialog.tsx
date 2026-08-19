import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { SimpleModal } from '@/design-system/SimpleModal/SimpleModal'

interface ComplementaryInfosDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  openNextDialog: (open: boolean) => void
  onCancel: () => void
}

export const ComplementaryInfosDialog = ({
  open,
  onOpenChange,
  openNextDialog,
  onCancel,
}: ComplementaryInfosDialogProps): JSX.Element => {
  return (
    <SimpleModal
      title="Informations complémentaires requises"
      isOpen={open}
      onClose={() => {
        onOpenChange(false)
        onCancel()
      }}
      actionButtons={[
        <Button
          onClick={() => {
            onOpenChange(false)
            onCancel()
          }}
          variant={ButtonVariant.SECONDARY}
          color={ButtonColor.BRAND}
          label={'Compléter plus tard'}
          key="cancel"
        />,
        <Button
          onClick={() => {
            onOpenChange(false)
            openNextDialog(true)
          }}
          variant={ButtonVariant.PRIMARY}
          color={ButtonColor.BRAND}
          label={'Compléter maintenant'}
          key="confirm"
        />,
      ]}
    >
      Pour confirmer l'accueil du public, quelques précisions sont nécessaires.
      Vous pouvez les saisir directement dans le volet latéral.
    </SimpleModal>
  )
}
