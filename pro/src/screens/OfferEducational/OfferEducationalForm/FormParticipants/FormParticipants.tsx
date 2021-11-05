import React from 'react'

import { Checkbox } from 'ui-kit'

import FormSection from '../FormSection'

import styles from './FormParticipants.module.scss'
import { participantsOptions } from './participantsOptions'


const FormParticipants = (): JSX.Element => {
  return (
    <FormSection
      subtitle="Votre offre s'adresse aux :"
      title='Informations participants'
    >
      <div className={styles['checkbox-group']}>
        {participantsOptions.map(({ label, value }) => (
          <Checkbox
            key={value}
            label={label}
            name='participants'
            value={value}
          />
        ))}
      </div>
    </FormSection>
  )
}

export default FormParticipants
