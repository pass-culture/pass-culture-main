import { useAnalytics } from '@/app/App/analytics/firebase'
import { BankAccountEvents } from '@/commons/core/FirebaseEvents/constants'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { ensureSelectedAdminOfferer } from '@/commons/store/user/selectors'
import {
  DS_BANK_ACCOUNT_PROCEDURE_ID,
  DS_NEW_CALEDONIA_BANK_ACCOUNT_PROCEDURE_ID,
} from '@/commons/utils/config'
import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'
import fullLinkIcon from '@/icons/full-link.svg'
import strokeLinkIcon from '@/icons/stroke-link.svg'
import { ConfirmDialog } from '@/ui-kit/ConfirmDialog/ConfirmDialog'

interface ReimbursmentPointDialogProps {
  closeDialog: () => void
  isDialogOpen: boolean
  dialogTriggerRef?: React.RefObject<HTMLButtonElement | null>
}

export const AddBankInformationsDialog = ({
  closeDialog,
  isDialogOpen,
  dialogTriggerRef,
}: ReimbursmentPointDialogProps) => {
  const { logEvent } = useAnalytics()
  const selectedAdminOfferer = useAppSelector(ensureSelectedAdminOfferer)

  return (
    <ConfirmDialog
      title="Vous allez être redirigé vers le site demarche.numerique.gouv.fr"
      icon={strokeLinkIcon}
      onCancel={closeDialog}
      open={isDialogOpen}
      refToFocusOnClose={dialogTriggerRef}
      overrideConfirm={
        <Button
          as="a"
          to={
            selectedAdminOfferer.isCaledonian
              ? DS_NEW_CALEDONIA_BANK_ACCOUNT_PROCEDURE_ID
              : DS_BANK_ACCOUNT_PROCEDURE_ID
          }
          isExternal={true}
          opensInNewTab={true}
          variant={ButtonVariant.PRIMARY}
          onClick={() => {
            logEvent(BankAccountEvents.CLICKED_CONTINUE_TO_DS)
          }}
          icon={fullLinkIcon}
          label={'Continuer sur demarche.numerique.gouv.fr'}
        />
      }
      cancelText={'Annuler'}
    >
      Démarche Numérique est une plateforme sécurisée de démarches
      administratives en ligne qui permet de déposer votre dossier de compte
      bancaire.
    </ConfirmDialog>
  )
}
