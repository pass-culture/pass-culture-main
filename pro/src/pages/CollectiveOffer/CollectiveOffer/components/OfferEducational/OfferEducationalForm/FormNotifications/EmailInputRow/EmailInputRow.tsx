import { forwardRef } from 'react'
import { useFormContext } from 'react-hook-form'

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
  name: string
  onDelete?: () => void
  autoFocus?: boolean
}

export const EmailInputRow = forwardRef<HTMLInputElement, EmailInputRowProps>(
  ({ disableForm, displayTrash = true, name, onDelete, autoFocus }, ref) => {
    const { register, getFieldState } = useFormContext()

    return (
      <FormLayout.Row className={styles['notification-mail']}>
        <TextInput
          label={NOTIFICATIONS_EMAIL_LABEL}
          disabled={disableForm}
          className={styles['notification-mail-input']}
          {...register(name)}
          ref={ref}
          autoFocus={autoFocus}
          required
          error={getFieldState(name).error?.message}
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
