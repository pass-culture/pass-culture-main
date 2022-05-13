import { Checkbox, TextInput } from 'ui-kit'
import {
  NOTIFICATIONS_EMAIL_LABEL,
  NOTIFICATIONS_LABEL,
} from '../../constants/labels'
import React, { useEffect } from 'react'

import FormLayout from 'new_components/FormLayout'
import { IOfferEducationalFormValues } from 'core/OfferEducational'
import { useFormikContext } from 'formik'

const FormNotifications = (): JSX.Element => {
  const { values, setFieldValue } =
    useFormikContext<IOfferEducationalFormValues>()

  useEffect(() => {
    if (values.notifications && values.email && !values.notificationEmail) {
      setFieldValue('notificationEmail', values.email)
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
        />
      </FormLayout.Row>
      {values.notifications && (
        <FormLayout.Row>
          <TextInput
            label={NOTIFICATIONS_EMAIL_LABEL}
            name="notificationEmail"
          />
        </FormLayout.Row>
      )}
    </FormLayout.Section>
  )
}

export default FormNotifications
