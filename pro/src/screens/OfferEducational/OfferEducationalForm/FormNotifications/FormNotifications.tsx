import { FieldArray, useFormikContext } from 'formik'
import React from 'react'

import FormLayout from 'components/FormLayout'
import { IOfferEducationalFormValues } from 'core/OfferEducational'
import { ReactComponent as PlusCircleIcon } from 'icons/ico-plus-circle.svg'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import EmailInputRow from './EmailInputRow/EmailInputRow'
import styles from './FormNotifications.module.scss'

const FormNotifications = ({
  disableForm,
}: {
  disableForm: boolean
}): JSX.Element => {
  const { values } = useFormikContext<IOfferEducationalFormValues>()

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
              Icon={PlusCircleIcon}
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
