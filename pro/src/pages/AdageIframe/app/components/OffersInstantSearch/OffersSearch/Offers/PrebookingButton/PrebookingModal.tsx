import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { SimpleModal } from '@/design-system/SimpleModal/SimpleModal'
import strokePassIcon from '@/icons/stroke-pass.svg'

interface PrebookingModalProps {
  closeModal: () => void
  preBookCurrentStock: () => Promise<void>
  isPreview?: boolean
  isDialogOpen: boolean
}

export const PrebookingModal = ({
  closeModal,
  preBookCurrentStock,
  isPreview = false,
  isDialogOpen,
}: PrebookingModalProps): JSX.Element => {
  return (
    <SimpleModal
      iconPath={strokePassIcon}
      title="Êtes-vous sûr de vouloir préréserver ?"
      isOpen={isDialogOpen}
      onClose={closeModal}
      actionButtons={
        <>
          <Button
            onClick={closeModal}
            variant={ButtonVariant.SECONDARY}
            color={ButtonColor.NEUTRAL}
            label="Fermer"
          />
          <Button
            onClick={preBookCurrentStock}
            disabled={isPreview}
            label="Préréserver"
          />
        </>
      }
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
    </SimpleModal>
  )
}
