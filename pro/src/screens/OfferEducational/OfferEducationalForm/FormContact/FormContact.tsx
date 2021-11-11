import React from 'react'

import { TextInput } from 'ui-kit'

import { EMAIL_LABEL, PHONE_LABEL } from '../../constants/labels'
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
          label={PHONE_LABEL}
          name='phone'
        />
      </div>
      <div className={styles.subsection}>
        <TextInput
          label={EMAIL_LABEL}
          name='email'
        />
      </div>
    </FormSection>
  )
}

export default FormContact
