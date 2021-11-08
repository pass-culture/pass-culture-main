import React from 'react'

import { Checkbox, TextInput } from 'ui-kit'

import FormSection from '../FormSection'

import styles from './FormNotifications.module.scss'

const FormNotifications = (): JSX.Element => {
  return (
    <FormSection
      title="Notifications"
    >
      <Checkbox
        label="Être notifié par email des réservations"
        name='notifications'
        value=''
      />
      <div className={styles.subsection}>
        <TextInput
          label="Email auquel envoyer les notifications"
          name='notificationEmail'
        />
      </div>
    </FormSection>
  )
}

export default FormNotifications
