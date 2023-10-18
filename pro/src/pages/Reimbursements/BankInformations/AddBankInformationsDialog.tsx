import React from 'react'

import Dialog from 'components/Dialog/Dialog'
import strokeLinkIcon from 'icons/stroke-link.svg'
import { ButtonLink } from 'ui-kit/Button'
import { DS_BANK_ACCOUNT_PROCEDURE_ID } from 'utils/config'

import styles from './AddBankInformationsDialog.module.scss'

interface ReimbursmentPointDialogProps {
  closeDialog: () => void
}

const AddBankInformationsDialog = ({
  closeDialog,
}: ReimbursmentPointDialogProps) => (
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
        rel: 'noopener noreferrer',
        target: '_blank',
      }}
      className={styles['link-button']}
    >
      Continuer sur demarches-simplifiees.fr
    </ButtonLink>
  </Dialog>
)

export default AddBankInformationsDialog
