import { useRef, useState } from 'react'

import { ConfirmDialog } from '@/components/ConfirmDialog/ConfirmDialog'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { Checkbox } from '@/design-system/Checkbox/Checkbox'
import { Callout } from '@/ui-kit/Callout/Callout'
import { CalloutVariant } from '@/ui-kit/Callout/types'

import styles from './UpdateWarningDialog.module.scss'

interface UpdateWarningDialogProps {
  onCancel: () => void
  onConfirm: (shouldSendWithdrawalMail: boolean) => void
}
export const UpdateWarningDialog = ({
  onCancel,
  onConfirm,
}: UpdateWarningDialogProps): JSX.Element => {
  const saveEditionChangesButtonRef = useRef<HTMLButtonElement>(null)

  const [shouldSendWithdrawalMail, setShouldSendWithdrawalMail] = useState(true)

  return (
    <ConfirmDialog
      cancelText="Annuler"
      confirmText="Je confirme le changement"
      onCancel={onCancel}
      onConfirm={() => onConfirm(shouldSendWithdrawalMail)}
      open
      title="Les changements vont s’appliquer à l’ensemble des réservations en cours associées"
      refToFocusOnClose={saveEditionChangesButtonRef}
    >
      <div className={styles['update-oa-wrapper']}>
        <div>Vous avez modifié la localisation.</div>

        <Callout variant={CalloutVariant.WARNING}>
          Si vous souhaitez que les réservations en cours conservent les données
          actuelles, veuillez créer une nouvelle offre avec les nouvelles
          informations.
        </Callout>

        <FormLayout.Row>
          <Checkbox
            label="Prévenir les jeunes par e-mail"
            onChange={(evt) => setShouldSendWithdrawalMail(evt.target.checked)}
            checked={shouldSendWithdrawalMail}
          />
        </FormLayout.Row>
      </div>
    </ConfirmDialog>
  )
}
