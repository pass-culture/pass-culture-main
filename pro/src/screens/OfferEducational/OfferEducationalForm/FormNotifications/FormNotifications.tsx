import { useFormikContext } from 'formik'
import React, { useEffect } from 'react'

import { IOfferEducationalFormValues } from 'core/OfferEducational'
import FormLayout from 'new_components/FormLayout'
import { Checkbox } from 'ui-kit'

import { NOTIFICATIONS_LABEL } from '../../constants/labels'

import EmailInputRow from './EmailInputRow/EmailInputRow'

const FormNotifications = ({
  disableForm,
}: {
  disableForm: boolean
}): JSX.Element => {
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
          disabled={disableForm}
        />
      </FormLayout.Row>
      {values.notifications && (
        <EmailInputRow
          disableForm={disableForm}
          displayTrash={false}
          name={'notificationEmail'}
        />
      )}
    </FormLayout.Section>
  )
}

export default FormNotifications
