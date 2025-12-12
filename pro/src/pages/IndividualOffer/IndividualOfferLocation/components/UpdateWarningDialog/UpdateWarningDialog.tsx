import { useState } from 'react'

import { ConfirmDialog } from '@/components/ConfirmDialog/ConfirmDialog'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { Banner, BannerVariants } from '@/design-system/Banner/Banner'
import { Checkbox } from '@/design-system/Checkbox/Checkbox'

import styles from './UpdateWarningDialog.module.scss'

interface UpdateWarningDialogProps {
  onCancel: () => void
  onConfirm: (shouldSendMail: boolean) => void
  refToFocusOnClose?: React.RefObject<HTMLButtonElement>
  message?: string
}
export const UpdateWarningDialog = ({
  onCancel,
  onConfirm,
  refToFocusOnClose,
  message,
}: UpdateWarningDialogProps): JSX.Element => {
  const [shouldSendMail, setShouldSendMail] = useState(true)

  return (
    <ConfirmDialog
      cancelText="Annuler"
      confirmText="Je confirme le changement"
      onCancel={onCancel}
      onConfirm={() => onConfirm(shouldSendMail)}
      open
      title="Les changements vont s’appliquer à l’ensemble des réservations en cours associées"
      refToFocusOnClose={refToFocusOnClose}
    >
      <div className={styles['update-oa-wrapper']}>
        <div>{message ?? 'Vous avez modifié la localisation.'}</div>

        <Banner
          title="Réservations en cours"
          variant={BannerVariants.WARNING}
          description="Pour conserver les données des réservations actuelles, créez une nouvelle offre avec vos modifications."
        ></Banner>

        <FormLayout.Row>
          <Checkbox
            label="Prévenir les jeunes par e-mail"
            onChange={(evt) => setShouldSendMail(evt.target.checked)}
            checked={shouldSendMail}
          />
        </FormLayout.Row>
      </div>
    </ConfirmDialog>
  )
}
