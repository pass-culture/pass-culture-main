import { useAnalytics } from '@/app/App/analytics/firebase'
import { BankAccountEvents } from '@/commons/core/FirebaseEvents/constants'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useIsCaledonian } from '@/commons/hooks/useIsCaledonian'
import {
  DS_BANK_ACCOUNT_PROCEDURE_ID,
  DS_NEW_CALEDONIA_BANK_ACCOUNT_PROCEDURE_ID,
} from '@/commons/utils/config'
import strokeLinkIcon from '@/icons/stroke-link.svg'
import { RedirectDialog } from '@/ui-kit/RedirectDialog/RedirectDialog'

interface ReimbursmentPointDialogProps {
  closeDialog: () => void
  offererId?: number
  isDialogOpen: boolean
  dialogTriggerRef?: React.RefObject<HTMLButtonElement | null>
}

export const AddBankInformationsDialog = ({
  closeDialog,
  offererId,
  isDialogOpen,
  dialogTriggerRef,
}: ReimbursmentPointDialogProps) => {
  const { logEvent } = useAnalytics()
  const withSwitchVenueFeature = useActiveFeature('WIP_SWITCH_VENUE')
  const isCaledonian = useIsCaledonian(withSwitchVenueFeature)

  return (
    <RedirectDialog
      title="Vous allez être redirigé vers le site demarche.numerique.gouv.fr"
      icon={strokeLinkIcon}
      onCancel={closeDialog}
      open={isDialogOpen}
      refToFocusOnClose={dialogTriggerRef}
      redirectText={'Continuer sur demarche.numerique.gouv.fr'}
      to={
        isCaledonian
          ? DS_NEW_CALEDONIA_BANK_ACCOUNT_PROCEDURE_ID
          : DS_BANK_ACCOUNT_PROCEDURE_ID
      }
      isExternal={true}
      onRedirect={() => {
        logEvent(BankAccountEvents.CLICKED_CONTINUE_TO_DS, {
          offererId,
        })
      }}
      cancelText={'Annuler'}
    >
      Démarche Numérique est une plateforme sécurisée de démarches
      administratives en ligne qui permet de déposer votre dossier de compte
      bancaire.
    </RedirectDialog>
  )
}
