import { FieldArray, useFormikContext } from 'formik'
import React, { useEffect } from 'react'

import { IOfferEducationalFormValues } from 'core/OfferEducational'
import { ReactComponent as PlusCircleIcon } from 'icons/ico-plus-circle.svg'
import { FormLayout } from 'new_components/FormLayout'
import { Button, Checkbox } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import { NOTIFICATIONS_LABEL } from '../../constants/labels'

import EmailInputRow from './EmailInputRow/EmailInputRow'
import styles from './FormNotifications.module.scss'

const FormNotifications = ({
  disableForm,
}: {
  disableForm: boolean
}): JSX.Element => {
  const { values, setFieldValue } =
    useFormikContext<IOfferEducationalFormValues>()

  useEffect(() => {
    if (values.notifications && values.email && !values.notificationEmails[0]) {
      setFieldValue('notificationEmails.0', values.email)
    }
  }, [values.notifications, setFieldValue])

  return (
    <FormLayout.Section title="Notifications">
      <FormLayout.Row>
        <Checkbox
          hideFooter
          label={NOTIFICATIONS_LABEL}
          name="notifications"
          value=""
          disabled={disableForm}
        />
      </FormLayout.Row>
      {values.notifications && (
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
                Ajouter un e-mail de notification
              </Button>
            </>
          )}
        </FieldArray>
      )}
    </FormLayout.Section>
  )
}

export default FormNotifications
