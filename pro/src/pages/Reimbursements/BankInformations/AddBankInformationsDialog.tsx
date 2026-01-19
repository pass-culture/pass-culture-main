import { useAnalytics } from '@/app/App/analytics/firebase'
import { BankAccountEvents } from '@/commons/core/FirebaseEvents/constants'
import { useIsCaledonian } from '@/commons/hooks/useIsCaledonian'
import {
  DS_BANK_ACCOUNT_PROCEDURE_ID,
  DS_NEW_CALEDONIA_BANK_ACCOUNT_PROCEDURE_ID,
} from '@/commons/utils/config'
import { Dialog } from '@/components/Dialog/Dialog'
import { Button } from '@/design-system/Button/Button'
import fullLinkIcon from '@/icons/full-link.svg'
import strokeLinkIcon from '@/icons/stroke-link.svg'

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
  const isCaledonian = useIsCaledonian()

  return (
    <Dialog
      title="Vous allez être redirigé vers le site demarche.numerique.gouv.fr"
      explanation="Démarche Numérique est une plateforme sécurisée de démarches administratives en ligne qui permet de déposer votre dossier de compte bancaire."
      icon={strokeLinkIcon}
      onCancel={closeDialog}
      open={isDialogOpen}
      refToFocusOnClose={dialogTriggerRef}
    >
      <div className={styles['link-button']}>
        <Button
          as="a"
          to={
            isCaledonian
              ? DS_NEW_CALEDONIA_BANK_ACCOUNT_PROCEDURE_ID
              : DS_BANK_ACCOUNT_PROCEDURE_ID
          }
          isExternal
          opensInNewTab
          icon={fullLinkIcon}
          onClick={() => {
            logEvent(BankAccountEvents.CLICKED_CONTINUE_TO_DS, {
              offererId,
            })
          }}
          label="Continuer sur demarche.numerique.gouv.fr"
        />
      </div>
    </Dialog>
  )
}
