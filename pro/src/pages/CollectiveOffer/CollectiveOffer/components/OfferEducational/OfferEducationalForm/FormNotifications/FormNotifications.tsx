import { FieldArray, useFormikContext } from 'formik'
import { useRef } from 'react'

import { OfferEducationalFormValues } from 'commons/core/OfferEducational/types'
import { FormLayout } from 'components/FormLayout/FormLayout'
import fullMoreIcon from 'icons/full-more.svg'
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
  const { values } = useFormikContext<OfferEducationalFormValues>()
  const inputRefs = useRef<(HTMLInputElement | null)[]>([])

  return (
    <FormLayout.Section title="À quel email le pass Culture peut-il vous envoyer des notifications ?">
      <FieldArray name="notificationEmails">
        {({ remove, push }) => (
          <>
            {values.notificationEmails?.map((email, index, self) => (
              <EmailInputRow
                disableForm={disableForm}
                displayTrash={index > 0}
                name={`notificationEmails.${index}`}
                key={`notificationEmails.${index}`}
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
                  self.length - 1 === index && self.length > 1 && email === ''
                }
              />
            ))}
            <Button
              variant={ButtonVariant.TERNARY}
              icon={fullMoreIcon}
              onClick={() => {
                push('')
              }}
              disabled={
                (values.notificationEmails &&
                  values.notificationEmails.length >= 5) ||
                disableForm
              }
              className={styles['add-notification-button']}
            >
              Ajouter un email de notification
            </Button>
          </>
        )}
      </FieldArray>
    </FormLayout.Section>
  )
}
