import { useAnalytics } from '@/app/App/analytics/firebase'
import { BankAccountEvents } from '@/commons/core/FirebaseEvents/constants'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useIsCaledonian } from '@/commons/hooks/useIsCaledonian'
import {
  DS_BANK_ACCOUNT_PROCEDURE_ID,
  DS_NEW_CALEDONIA_BANK_ACCOUNT_PROCEDURE_ID,
} from '@/commons/utils/config'
import { Dialog } from '@/components/Dialog/Dialog'
import fullLinkIcon from '@/icons/full-link.svg'
import strokeLinkIcon from '@/icons/stroke-link.svg'
import { ButtonLink } from '@/ui-kit/Button/ButtonLink'
import { ButtonVariant } from '@/ui-kit/Button/types'

import styles from './AddBankInformationsDialog.module.scss'

interface ReimbursmentPointDialogProps {
  closeDialog: () => void
  offererId?: number
  isDialogOpen: boolean
  dialogTriggerRef?: React.RefObject<HTMLButtonElement>
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
    <Dialog
      title="Vous allez être redirigé vers le site demarche.numerique.gouv.fr"
      explanation="Démarche Numérique est une plateforme sécurisée de démarches administratives en ligne qui permet de déposer votre dossier de compte bancaire."
      icon={strokeLinkIcon}
      onCancel={closeDialog}
      open={isDialogOpen}
      refToFocusOnClose={dialogTriggerRef}
    >
      <ButtonLink
        to={
          isCaledonian
            ? DS_NEW_CALEDONIA_BANK_ACCOUNT_PROCEDURE_ID
            : DS_BANK_ACCOUNT_PROCEDURE_ID
        }
        isExternal
        opensInNewTab
        icon={fullLinkIcon}
        className={styles['link-button']}
        variant={ButtonVariant.PRIMARY}
        onClick={() => {
          logEvent(BankAccountEvents.CLICKED_CONTINUE_TO_DS, {
            offererId,
          })
        }}
      >
        Continuer sur demarche.numerique.gouv.fr
      </ButtonLink>
    </Dialog>
  )
}
