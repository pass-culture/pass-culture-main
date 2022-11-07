import { useFormikContext } from 'formik'
import React, { useEffect } from 'react'

import FormLayout from 'components/FormLayout'
import useCurrentUser from 'hooks/useCurrentUser'
import { Checkbox, TextInput } from 'ui-kit'

import { IOfferIndividualFormValues } from '../types'

import { NOTIFICATIONS_DEFAULT_VALUES } from './constants'

const Notifications = (): JSX.Element => {
  const { currentUser } = useCurrentUser()
  const {
    values: { receiveNotificationEmails, bookingEmail },
    setFieldValue,
  } = useFormikContext<IOfferIndividualFormValues>()

  useEffect(() => {
    if (
      receiveNotificationEmails &&
      bookingEmail === NOTIFICATIONS_DEFAULT_VALUES.bookingEmail
    ) {
      setFieldValue('bookingEmail', currentUser.email)
    }
  }, [receiveNotificationEmails])

  return (
    <FormLayout.Section title="Notifications">
      <FormLayout.Row>
        <Checkbox
          label="Être notifié par e-mail des réservations"
          name="receiveNotificationEmails"
          value=""
          hideFooter={receiveNotificationEmails}
        />
      </FormLayout.Row>

      {receiveNotificationEmails && (
        <FormLayout.Row>
          <TextInput
            label="E-mail auquel envoyer les notifications"
            maxLength={90}
            name="bookingEmail"
            placeholder="email@exemple.com"
          />
        </FormLayout.Row>
      )}
    </FormLayout.Section>
  )
}

export default Notifications
