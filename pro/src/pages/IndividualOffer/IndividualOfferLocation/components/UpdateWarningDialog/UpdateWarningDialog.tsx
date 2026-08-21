import fullClearIcon from 'icons/full-clear.svg'
import strokeWarningIcon from 'icons/stroke-warning.svg'

import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
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
  return (
    <SimpleModal
      title="Les changements vont impacter l’ensemble des réservations en cours associées"
      isOpen={isOpen}
      onClose={onCancel}
      iconPath={strokeWarningIcon}
      iconClassName={styles['update-oa-icon']}
      actionButtons={[
        <Button
          onClick={onCancel}
          variant={ButtonVariant.TERTIARY}
          color={ButtonColor.NEUTRAL}
          icon={fullClearIcon}
          label={'Annuler'}
          key="cancel"
        />,
        <Button
          onClick={() => onConfirm(false)}
          variant={ButtonVariant.SECONDARY}
          color={ButtonColor.NEUTRAL}
          label={'Ne pas prévenir les jeunes'}
          key="no-notify"
        />,
        <Button
          onClick={() => onConfirm(true)}
          variant={ButtonVariant.PRIMARY}
          color={ButtonColor.BRAND}
          label={'Prévenir les jeunes'}
          key="notify"
        />,
      ]}
    >
      <div className={styles['update-oa-wrapper']}>
        <p>
          {message}&nbsp;
          <strong>Souhaitez-vous prévenir les jeunes par mail ?</strong>
        </p>
      </div>
    </SimpleModal>
  )
}
