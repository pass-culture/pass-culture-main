import { OfferEducationalFormValues } from 'commons/core/OfferEducational/types'
import { FormLayout } from 'components/FormLayout/FormLayout'
import fullMoreIcon from 'icons/full-more.svg'
import { useRef } from 'react'
import { useFieldArray, useFormContext } from 'react-hook-form'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'

import { EmailInputRow } from './EmailInputRow/EmailInputRow'
import styles from './FormNotifications.module.scss'

interface FormNotificationsProps {
  disableForm: boolean
}

export const FormNotifications = ({
  disableForm,
}: FormNotificationsProps): JSX.Element => {
  const { watch, getFieldState, setValue } =
    useFormContext<OfferEducationalFormValues>()
  const { fields, remove, append } = useFieldArray({
    name: 'notificationEmails',
  })
  const inputRefs = useRef<(HTMLInputElement | null)[]>([])

  const emails = watch('notificationEmails') || []

  return (
    <FormLayout.Section
      title="À quel email le pass Culture peut-il vous envoyer des notifications ?"
      className={styles['emails']}
    >
      {fields.map((field, index) => (
        <EmailInputRow
          disableForm={disableForm}
          key={field.id}
          displayTrash={index > 0}
          email={watch(`notificationEmails.${index}.email`)}
          onChange={(e) =>
            setValue(`notificationEmails.${index}.email`, e.target.value, {
              shouldValidate: true,
            })
          }
          error={
            getFieldState(`notificationEmails.${index}.email`).error?.message
          }
          ref={(el) => (inputRefs.current[index] = el)}
          onDelete={() => {
            const newIndex = index - 1
            inputRefs.current[newIndex]?.focus()

            remove(index)
          }}
          //  The field should autoFocus only if it's the last of the emails list (the one being just added)
          //  if the list has more than one emails (the first one is always there and cannot appear)
          //  and if that last email is empty (otherwise it would focus the last email in an edition form with more than one email)
          autoFocus={
            self.length - 1 === index && self.length > 1 && !emails[index].email
          }
        />
      ))}
      {!disableForm && emails.length <= 5 && (
        <Button
          variant={ButtonVariant.TERNARY}
          icon={fullMoreIcon}
          onClick={() => {
            append({ email: '' })
          }}
          className={styles['add-notification-button']}
        >
          Ajouter un email de notification
        </Button>
      )}
    </FormLayout.Section>
  )
}
