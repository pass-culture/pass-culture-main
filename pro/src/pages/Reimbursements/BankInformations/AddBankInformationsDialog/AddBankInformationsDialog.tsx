import { useAnalytics } from '@/app/App/analytics/firebase'
import { BankAccountEvents } from '@/commons/core/FirebaseEvents/constants'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { ensureSelectedAdminOfferer } from '@/commons/store/user/selectors'
import {
  DS_BANK_ACCOUNT_PROCEDURE_ID,
  DS_NEW_CALEDONIA_BANK_ACCOUNT_PROCEDURE_ID,
} from '@/commons/utils/config'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { SimpleModal } from '@/design-system/SimpleModal/SimpleModal'
import fullLinkIcon from '@/icons/full-link.svg'
import strokeLinkIcon from '@/icons/stroke-link.svg'

import styles from './AddBankInformationsDialog.module.scss'

interface ReimbursmentPointDialogProps {
  closeDialog: () => void
  isDialogOpen: boolean
}

export const AddBankInformationsDialog = ({
  closeDialog,
  isDialogOpen,
}: ReimbursmentPointDialogProps) => {
  const { logEvent } = useAnalytics()
  const selectedAdminOfferer = useAppSelector(ensureSelectedAdminOfferer)

  return (
    <SimpleModal
      title="Vous allez être redirigé vers le site demarche.numerique.gouv.fr"
      iconPath={strokeLinkIcon}
      isOpen={isDialogOpen}
      onClose={closeDialog}
      actionButtons={[
        <Button
          onClick={closeDialog}
          variant={ButtonVariant.SECONDARY}
          color={ButtonColor.NEUTRAL}
          label="Annuler"
          key="cancel"
        />,
        <span className={styles['continue-button']} key="continue">
          <Button
            as="a"
            to={
              selectedAdminOfferer.isCaledonian
                ? DS_NEW_CALEDONIA_BANK_ACCOUNT_PROCEDURE_ID
                : DS_BANK_ACCOUNT_PROCEDURE_ID
            }
            opensInNewTab={true}
            variant={ButtonVariant.PRIMARY}
            onClick={() => {
              logEvent(BankAccountEvents.CLICKED_CONTINUE_TO_DS)
            }}
            icon={fullLinkIcon}
            label="Continuer sur demarche.numerique.gouv.fr"
          />
        </span>,
      ]}
    >
      <p>
        Démarche Numérique est une plateforme sécurisée de démarches
        administratives en ligne qui permet de déposer votre dossier de compte
        bancaire.
      </p>
    </SimpleModal>
  )
}
