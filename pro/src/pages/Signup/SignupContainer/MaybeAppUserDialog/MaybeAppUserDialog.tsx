import { RedirectDialog } from '@/components/RedirectDialog/RedirectDialog'
import strokeFraudIcon from '@/icons/stroke-fraud.svg'

export const MaybeAppUserDialog = ({
  onCancel,
  isDialogOpen,
}: {
  onCancel: () => void
  isDialogOpen: boolean
}) => {
  return (
    <RedirectDialog
      icon={strokeFraudIcon}
      redirectText="S’inscrire sur l’application pass Culture"
      redirectLink={{
        to: 'https://passculture.app/',
        isExternal: true,
      }}
      cancelText="Continuer vers le pass Culture Pro"
      title="Il semblerait que tu ne sois pas"
      secondTitle={` un professionnel de la culture`}
      onCancel={onCancel}
      open={isDialogOpen}
    >
      <p>
        Tu essayes de t’inscrire sur l’espace pass Culture Pro dédié aux
        professionnels de la culture. Pour créer ton compte, rends-toi sur
        l’application pass Culture.
      </p>
    </RedirectDialog>
  )
}
