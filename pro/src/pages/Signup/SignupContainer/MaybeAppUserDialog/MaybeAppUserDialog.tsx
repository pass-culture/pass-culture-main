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
      redirectLink={{
        to: 'https://passculture.app/',
        isExternal: true,
      }}
      cancelText="Continuer vers le pass Culture Pro"
      title="Il semblerait que tu ne sois pas"
      secondTitle={` un professionnel de la culture`}
      onCancel={onCancel}
      onClose={onClose}
      open={isDialogOpen}
    >
      {isHigherEducation ? (
        <p>
          Vous vous apprêtez à rejoindre l’espace pass Culture pro d’un
          établissement d’enseignement supérieur. Seuls les professionnels sont
          habilités à rejoindre cet espace.
          <br />
          Si vous n’êtes pas un professionnel, nous vous invitons à créer votre
          compte sur l’application pass Culture.
          <br />
          Pour information, conformément aux critères d’éligibilité, les bureaux
          d’élèves et les associations étudiantes ne sont pas reconnus comme
          professionnels de la culture sur le dispositif pass Culture.
        </p>
      ) : (
        <p>
          Tu essayes de t’inscrire sur l’espace pass Culture Pro dédié aux
          professionnels de la culture. Pour créer ton compte, rends-toi sur
          l’application pass Culture.
        </p>
      )}
    </RedirectDialog>
  )
}
