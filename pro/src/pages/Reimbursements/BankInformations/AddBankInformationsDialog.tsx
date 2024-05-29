import React from 'react'

import { useAnalytics } from 'app/App/analytics/firebase'
import { Dialog } from 'components/Dialog/Dialog/Dialog'
import { BankAccountEvents } from 'core/FirebaseEvents/constants'
import fullLinkIcon from 'icons/full-link.svg'
import strokeLinkIcon from 'icons/stroke-link.svg'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { DS_BANK_ACCOUNT_PROCEDURE_ID } from 'utils/config'

import styles from './AddBankInformationsDialog.module.scss'

interface ReimbursmentPointDialogProps {
  closeDialog: () => void
  offererId?: number
}

export const AddBankInformationsDialog = ({
  closeDialog,
  offererId,
}: ReimbursmentPointDialogProps) => {
  const { logEvent } = useAnalytics()
  return (
    <Dialog
      title="Vous allez être redirigé vers le site demarches-simplifiees.fr"
      explanation="Démarches Simplifiées est une plateforme sécurisée de démarches administratives en ligne qui permet de déposer votre dossier de compte bancaire."
      icon={strokeLinkIcon}
      onCancel={closeDialog}
    >
      <ButtonLink
        link={{
          to: DS_BANK_ACCOUNT_PROCEDURE_ID,
          isExternal: true,
          target: '_blank',
        }}
        icon={fullLinkIcon}
        className={styles['link-button']}
        variant={ButtonVariant.PRIMARY}
        svgAlt="Nouvelle fenêtre"
        onClick={() => {
          logEvent(BankAccountEvents.CLICKED_CONTINUE_TO_DS, {
            offererId,
          })
        }}
      >
        Continuer sur demarches-simplifiees.fr
      </ButtonLink>
    </Dialog>
  )
}
