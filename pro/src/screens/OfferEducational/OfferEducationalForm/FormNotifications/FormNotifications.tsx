import React from 'react'

import FormLayout from 'new_components/FormLayout'
import { Checkbox, TextInput } from 'ui-kit'

import {
  NOTIFICATIONS_EMAIL_LABEL,
  NOTIFICATIONS_LABEL,
} from '../../constants/labels'

const FormNotifications = (): JSX.Element => (
  <FormLayout.Section title="Notifications">
    <FormLayout.Row>
      <Checkbox label={NOTIFICATIONS_LABEL} name="notifications" value="" />
    </FormLayout.Row>
    <FormLayout.Row>
      <TextInput label={NOTIFICATIONS_EMAIL_LABEL} name="notificationEmail" />
    </FormLayout.Row>
  </FormLayout.Section>
)

export default FormNotifications
