import { useFormikContext } from 'formik'
import React, { useEffect } from 'react'

import FormLayout from 'components/FormLayout'
import useCurrentUser from 'hooks/useCurrentUser'
import { Checkbox, TextInput } from 'ui-kit'

import { IOfferIndividualFormValues } from '../types'

import { NOTIFICATIONS_DEFAULT_VALUES } from './constants'

export interface INotifications {
  venueBookingEmail?: string | null
  readOnlyFields?: string[]
}

const Notifications = ({
  readOnlyFields,
  venueBookingEmail,
}: INotifications): JSX.Element => {
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
      setFieldValue('bookingEmail', venueBookingEmail ?? currentUser.email)
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
          disabled={readOnlyFields?.includes('receiveNotificationEmails')}
        />
      </FormLayout.Row>

      {receiveNotificationEmails && (
        <FormLayout.Row>
          <TextInput
            label="E-mail auquel envoyer les notifications"
            maxLength={90}
            name="bookingEmail"
            placeholder="email@exemple.com"
            disabled={readOnlyFields?.includes('bookingEmail')}
          />
        </FormLayout.Row>
      )}
    </FormLayout.Section>
  )
}

export default Notifications
