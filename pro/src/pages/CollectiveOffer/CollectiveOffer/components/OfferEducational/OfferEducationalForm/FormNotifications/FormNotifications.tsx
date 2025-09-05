import { useFieldArray, useFormContext } from 'react-hook-form'

import type { OfferEducationalFormValues } from '@/commons/core/OfferEducational/types'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { TextInput } from '@/design-system/TextInput/TextInput'
import fullMoreIcon from '@/icons/full-more.svg'
import fullTrashIcon from '@/icons/full-trash.svg'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonVariant } from '@/ui-kit/Button/types'
import { ListIconButton } from '@/ui-kit/ListIconButton/ListIconButton'

import { NOTIFICATIONS_EMAIL_LABEL } from '../../constants/labels'
import styles from './FormNotifications.module.scss'

interface FormNotificationsProps {
  disableForm: boolean
}

export const FormNotifications = ({
  disableForm,
}: FormNotificationsProps): JSX.Element => {
  const { getFieldState, setFocus, register } =
    useFormContext<OfferEducationalFormValues>()
  const { fields, remove, append } = useFieldArray({
    name: 'notificationEmails',
  })

  return (
    <FormLayout.Section
      title="À quel email le pass Culture peut-il vous envoyer des notifications ?"
      className={styles['emails']}
    >
      {fields.map((field, index) => (
        <FormLayout.Row className={styles['notification-mail']} key={field.id}>
          <div className={styles['notification-mail-input']}>
            <TextInput
              label={NOTIFICATIONS_EMAIL_LABEL}
              disabled={disableForm}
              required
              {...register(`notificationEmails.${index}.email`)}
              error={
                getFieldState(`notificationEmails.${index}.email`).error
                  ?.message
              }
              description="Format : email@exemple.com"
              extension={
                index > 0 &&
                !disableForm && (
                  <ListIconButton
                    onClick={() => {
                      remove(index)
                      setFocus(`notificationEmails.${index - 1}.email`)
                    }}
                    icon={fullTrashIcon}
                    tooltipContent="Supprimer l’email"
                  />
                )
              }
            />
          </div>
        </FormLayout.Row>
      ))}
      {!disableForm && fields.length <= 5 && (
        <Button
          variant={ButtonVariant.TERNARY}
          icon={fullMoreIcon}
          onClick={() => {
            append({ email: '' }, { shouldFocus: true })
          }}
          className={styles['add-notification-button']}
        >
          Ajouter un email de notification
        </Button>
      )}
    </FormLayout.Section>
  )
}
