import { ChangeEvent, forwardRef } from 'react'

import { FormLayout } from 'components/FormLayout/FormLayout'
import fullTrashIcon from 'icons/full-trash.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'
import { TextInput } from 'ui-kit/formV2/TextInput/TextInput'

import { NOTIFICATIONS_EMAIL_LABEL } from '../../../constants/labels'

import styles from './EmailInputRow.module.scss'

interface EmailInputRowProps {
  disableForm: boolean
  displayTrash?: boolean
  onDelete?: () => void
  email: string
  autoFocus?: boolean
  error?: string
  onChange: (e: ChangeEvent<HTMLInputElement>) => void
}

export const EmailInputRow = forwardRef<HTMLInputElement, EmailInputRowProps>(
  (
    {
      disableForm,
      displayTrash = true,
      onDelete,
      autoFocus,
      email,
      error,
      onChange,
    },
    ref
  ) => {
    return (
      <FormLayout.Row className={styles['notification-mail']}>
        <TextInput
          label={NOTIFICATIONS_EMAIL_LABEL}
          disabled={disableForm}
          className={styles['notification-mail-input']}
          ref={ref}
          autoFocus={autoFocus}
          required
          value={email || ''}
          name="email-input"
          error={error}
          onChange={onChange}
          description="Format : email@exemple.com"
        />
        {displayTrash && !disableForm && (
          <div className={styles['trash']}>
            <Button
              onClick={onDelete}
              icon={fullTrashIcon}
              iconPosition={IconPositionEnum.CENTER}
              variant={ButtonVariant.TERNARY}
              tooltipContent="Supprimer l’email"
            />
          </div>
        )}
      </FormLayout.Row>
    )
  }
)

EmailInputRow.displayName = 'EmailInputRow'
