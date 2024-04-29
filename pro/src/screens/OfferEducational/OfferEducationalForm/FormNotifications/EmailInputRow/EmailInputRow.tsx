import React from 'react'

import { FormLayout } from 'components/FormLayout/FormLayout'
import fullTrashIcon from 'icons/full-trash.svg'
import { NOTIFICATIONS_EMAIL_LABEL } from 'screens/OfferEducational/constants/labels'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'

import styles from './EmailInputRow.module.scss'

interface EmailInputRowProps {
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
}: EmailInputRowProps) => {
  return (
    <FormLayout.Row inline className={styles['notification-mail']}>
      <TextInput
        label={NOTIFICATIONS_EMAIL_LABEL}
        name={name}
        disabled={disableForm}
        className={styles['notification-mail-input']}
      />
      {displayTrash && (
        <div className={styles['trash']}>
          <Button
            onClick={onDelete}
            icon={fullTrashIcon}
            iconPosition={IconPositionEnum.CENTER}
            variant={ButtonVariant.TERNARY}
            hasTooltip
          >
            Supprimer l’email
          </Button>
        </div>
      )}
    </FormLayout.Row>
  )
}

export default EmailInputRow
