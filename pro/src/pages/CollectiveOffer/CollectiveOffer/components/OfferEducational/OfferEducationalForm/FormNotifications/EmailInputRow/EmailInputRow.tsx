import { forwardRef } from 'react'

import { FormLayout } from 'components/FormLayout/FormLayout'
import fullTrashIcon from 'icons/full-trash.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'
import { Tooltip } from 'ui-kit/Tooltip/Tooltip'

import { NOTIFICATIONS_EMAIL_LABEL } from '../../../constants/labels'

import styles from './EmailInputRow.module.scss'

interface EmailInputRowProps {
  disableForm: boolean
  displayTrash?: boolean
  name: string
  onDelete?: () => void
  autoFocus?: boolean
}

export const EmailInputRow = forwardRef<HTMLInputElement, EmailInputRowProps>(
  ({ disableForm, displayTrash = true, name, onDelete, autoFocus }, ref) => {
    return (
      <FormLayout.Row className={styles['notification-mail']}>
        <TextInput
          label={NOTIFICATIONS_EMAIL_LABEL}
          name={name}
          disabled={disableForm}
          className={styles['notification-mail-input']}
          focusRef={ref}
          autoFocus={autoFocus}
          description="Format : email@exemple.com"
        />
        {displayTrash && (
          <div className={styles['trash']}>
            <Tooltip content="Supprimer l’email">
              <Button
                onClick={onDelete}
                icon={fullTrashIcon}
                iconPosition={IconPositionEnum.CENTER}
                variant={ButtonVariant.TERNARY}
                disabled={disableForm}
              />
            </Tooltip>
          </div>
        )}
      </FormLayout.Row>
    )
  }
)

EmailInputRow.displayName = 'EmailInputRow'
