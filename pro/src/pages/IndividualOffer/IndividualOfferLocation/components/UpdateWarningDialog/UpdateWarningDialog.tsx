import { useState } from 'react'

import { FormLayout } from '@/components/FormLayout/FormLayout'
import { Banner, BannerVariants } from '@/design-system/Banner/Banner'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { Checkbox } from '@/design-system/Checkbox/Checkbox'
import { SimpleModal } from '@/design-system/SimpleModal/SimpleModal'

import styles from './UpdateWarningDialog.module.scss'

interface UpdateWarningDialogProps {
  onCancel: () => void
  onConfirm: (shouldSendMail: boolean) => void
  message?: string
  isOpen: boolean
}
export const UpdateWarningDialog = ({
  onCancel,
  onConfirm,
  message,
  isOpen,
}: UpdateWarningDialogProps): JSX.Element => {
  const [shouldSendMail, setShouldSendMail] = useState(true)

  return (
    <SimpleModal
      title="Les changements vont s’appliquer à l’ensemble des réservations en cours associées"
      isOpen={isOpen}
      onClose={onCancel}
      actionButtons={
        <>
          <Button
            onClick={onCancel}
            variant={ButtonVariant.SECONDARY}
            color={ButtonColor.NEUTRAL}
            label={'Annuler'}
          />
          <Button
            onClick={() => onConfirm(shouldSendMail)}
            variant={ButtonVariant.PRIMARY}
            color={ButtonColor.BRAND}
            label={'Je confirme le changement'}
          />
        </>
      }
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
    </SimpleModal>
  )
}
