import { useFormikContext } from 'formik'
import React, { useEffect } from 'react'

import useCurrentUser from 'components/hooks/useCurrentUser'
import FormLayout from 'new_components/FormLayout'
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
          label="Être notifié par email des réservations"
          name="receiveNotificationEmails"
          value=""
        />
      </FormLayout.Row>

      {receiveNotificationEmails && (
        <FormLayout.Row>
          <TextInput
            label="Email auquel envoyer les notifications :"
            maxLength={90}
            name="bookingEmail"
          />
        </FormLayout.Row>
      )}
    </FormLayout.Section>
  )
}

export default Notifications
