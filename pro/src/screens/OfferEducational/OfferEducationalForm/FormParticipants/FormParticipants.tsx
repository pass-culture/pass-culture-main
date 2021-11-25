import React from 'react'

import FormLayout from 'new_components/FormLayout'
import { Checkbox } from 'ui-kit'

import styles from './FormParticipants.module.scss'
import { participantsOptions } from './participantsOptions'

const FormParticipants = (): JSX.Element => {
  return (
    <FormLayout.Section
      description="Votre offre s'adresse aux :"
      title="Informations participants"
    >
      <div className={styles['checkbox-group']}>
        {participantsOptions.map(option => (
          <Checkbox
            key={option}
            label={option}
            name="participants"
            value={option}
          />
        ))}
      </div>
    </FormLayout.Section>
  )
}

export default FormParticipants
