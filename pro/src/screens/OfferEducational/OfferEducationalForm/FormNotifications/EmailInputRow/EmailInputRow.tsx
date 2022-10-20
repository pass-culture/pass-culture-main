import React from 'react'

import { ReactComponent as TrashFilledIcon } from 'icons/ico-trash-filled.svg'
import FormLayout from 'new_components/FormLayout'
import { NOTIFICATIONS_EMAIL_LABEL } from 'screens/OfferEducational/constants/labels'
import { Button, TextInput } from 'ui-kit'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'

import styles from './EmailInputRow.module.scss'

interface IEmailInputRowProps {
  disableForm: boolean
  displayTrash?: boolean
  name: string
  onDelete?: () => void
}

const EmailInputRow = ({
  disableForm,
  displayTrash = true,
  name,
  onDelete,
}: IEmailInputRowProps) => {
  return (
    <FormLayout.Row className={styles['notification-mail']}>
      <TextInput
        label={NOTIFICATIONS_EMAIL_LABEL}
        name={name}
        disabled={disableForm}
        className={styles['notification-mail-input']}
      />
      {displayTrash && (
        <Button
          onClick={onDelete}
          Icon={TrashFilledIcon}
          iconPosition={IconPositionEnum.CENTER}
          className={styles['trash']}
          variant={ButtonVariant.TERNARY}
          hasTooltip
        >
          Supprimer l'email
        </Button>
      )}
    </FormLayout.Row>
  )
}

export default EmailInputRow
