import { FieldArray, useFormikContext } from 'formik'
import React from 'react'

import FormLayout from 'components/FormLayout'
import { OfferEducationalFormValues } from 'core/OfferEducational'
import fullMoreIcon from 'icons/full-more.svg'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import EmailInputRow from './EmailInputRow/EmailInputRow'
import styles from './FormNotifications.module.scss'

interface FormNotificationsProps {
  disableForm: boolean
}

const FormNotifications = ({
  disableForm,
}: FormNotificationsProps): JSX.Element => {
  const { values } = useFormikContext<OfferEducationalFormValues>()

  return (
    <FormLayout.Section title="Notifications">
      <FieldArray name="notificationEmails">
        {({ remove, push }) => (
          <>
            {values.notificationEmails.map((_, index) => (
              <EmailInputRow
                disableForm={disableForm}
                displayTrash={index > 0}
                name={`notificationEmails.${index}`}
                key={`notificationEmails.${index}`}
                onDelete={() => {
                  remove(index)
                }}
              />
            ))}
            <Button
              variant={ButtonVariant.TERNARY}
              icon={fullMoreIcon}
              onClick={() => push('')}
              disabled={values.notificationEmails.length >= 5}
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

export default FormNotifications
