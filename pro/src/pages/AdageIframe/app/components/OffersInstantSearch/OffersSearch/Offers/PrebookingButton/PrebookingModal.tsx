import { ConfirmDialog } from '@/components/ConfirmDialog/ConfirmDialog'
import strokePassIcon from '@/icons/stroke-pass.svg'

interface PrebookingModalProps {
  closeModal: () => void
  preBookCurrentStock: () => Promise<void>
  isPreview?: boolean
  isDialogOpen: boolean
  refToFocusOnClose?: React.RefObject<HTMLElement>
}

export const PrebookingModal = ({
  closeModal,
  preBookCurrentStock,
  isPreview = false,
  isDialogOpen,
  refToFocusOnClose,
}: PrebookingModalProps): JSX.Element => {
  return (
    <ConfirmDialog
      icon={strokePassIcon}
      onConfirm={preBookCurrentStock}
      onCancel={closeModal}
      title="Êtes-vous sûr de vouloir préréserver ?"
      confirmText="Préréserver"
      cancelText="Fermer"
      confirmButtonDisabled={isPreview}
      open={isDialogOpen}
      refToFocusOnClose={refToFocusOnClose}
    >
      <p>
        Si oui, une fois votre préréservation confirmée :
        <br />
        <br />
        <strong>1) Rattachez votre préréservation à un projet </strong>: pour
        cela rendez-vous sous la rubrique <strong>Projets EAC</strong>, puis
        cliquez sur <strong>Les Projets </strong>
        pour créer un projet et rattacher votre préréservation à votre nouveau
        projet ou à un projet existant
        <br />
        <br />
        <strong>2)</strong> Votre chef d’établissement pourra alors{' '}
        <strong>confirmer la préréservation</strong>
      </p>
    </ConfirmDialog>
  )
}
