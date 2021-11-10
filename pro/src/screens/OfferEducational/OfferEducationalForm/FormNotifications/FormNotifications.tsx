import React from 'react'

import { Checkbox, TextInput } from 'ui-kit'

import { NOTIFICATIONS_EMAIL_LABEL, NOTIFICATIONS_LABEL } from '../../constants/labels'
import FormSection from '../FormSection'

import styles from './FormNotifications.module.scss'

const FormNotifications = (): JSX.Element => {
  return (
    <FormSection
      title="Notifications"
    >
      <Checkbox
        label={NOTIFICATIONS_LABEL}
        name='notifications'
        value=''
      />
      <div className={styles.subsection}>
        <TextInput
          label={NOTIFICATIONS_EMAIL_LABEL}
          name='notificationEmail'
        />
      </div>
    </FormSection>
  )
}

export default FormNotifications
