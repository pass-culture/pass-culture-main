import { useFormikContext } from 'formik'
import React, { useEffect } from 'react'

import { IOfferEducationalFormValues } from 'core/OfferEducational'
import FormLayout from 'new_components/FormLayout'
import { Checkbox, TextInput } from 'ui-kit'

import {
  NOTIFICATIONS_EMAIL_LABEL,
  NOTIFICATIONS_LABEL,
} from '../../constants/labels'

const FormNotifications = (): JSX.Element => {
  const { values, setFieldValue } =
    useFormikContext<IOfferEducationalFormValues>()

  useEffect(() => {
    if (values.notifications && values.email && !values.notificationEmail) {
      setFieldValue('notificationEmail', values.email)
    }
    // disable eslint because we want to trigger prefill only when checkbox value is updated
    // eslint-disable-next-line react-hooks/exhaustive-deps
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
