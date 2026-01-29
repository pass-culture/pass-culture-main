import { RedirectDialog } from '@/components/RedirectDialog/RedirectDialog'
import strokeFraudIcon from '@/icons/stroke-fraud.svg'

export const MaybeAppUserDialog = ({
  onCancel,
  onClose,
  isDialogOpen,
  isHigherEducation,
}: {
  onCancel: () => void
  onClose: () => void
  isDialogOpen: boolean
  isHigherEducation: boolean
}) => {
  return (
    <RedirectDialog
      icon={strokeFraudIcon}
      redirectText="S’inscrire sur l’application pass Culture"
      to="https://passculture.app/"
      isExternal={true}
      cancelText="Continuer vers le pass Culture Pro"
      title={
        isHigherEducation
          ? "Travaillez-vous pour un établissement d'enseignement supérieur ?"
          : 'Êtes-vous un professionnel de la culture ?'
      }
      onCancel={onCancel}
      onClose={onClose}
      open={isDialogOpen}
    >
      <p>
        Seuls les professionnels sont habilités à rejoindre l’espace pass
        Culture Pro. Si vous êtes un élève ou un jeune, créez directement votre
        compte sur l’application pass Culture
      </p>
    </RedirectDialog>
  )
}
