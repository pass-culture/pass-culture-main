import React from 'react'

import { TextInput } from 'ui-kit'

import FormSection from '../FormSection'

import styles from './FormContact.module.scss'

const FormContact = (): JSX.Element => {
  return (
    <FormSection
      subtitle="Ces informations seront affichées sur votre offre, pour permettre aux établissements scolaires de vous contacter"
      title="Contact"
    >
      <div className={styles.subsection}>
        <TextInput
          label="Téléphone"
          name='phone'
        />
      </div>
      <div className={styles.subsection}>
        <TextInput
          label="Email"
          name='email'
        />
      </div>
    </FormSection>
  )
}

export default FormContact
