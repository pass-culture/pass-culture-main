import React from 'react'

import { RadioButton } from 'ui-kit'

import FormSection from '../FormSection'

import styles from './FormOfferVenue.module.scss'

const FormOfferVenue = (): JSX.Element => {
  return (
    <FormSection
      subtitle="Ces informations seront visibles par les établissements scolaires"
      title="Informations pratiques"
    >
      <div className={styles.subsection}>
        <h4 className={styles.title}>
          Addresse où aura lieu l'événement
        </h4>
        <div className={styles['radio-group']}>
          <RadioButton
            label='Dans votre établissement'
            name='offerVenueId'
            value='offererVenue'
          />
          <RadioButton
            label="Dans l'établissement scolaire"
            name='offerVenueId'
            value='school'
          />
          <RadioButton
            label='Autre'
            name='offerVenueId'
            value='other'
          />
        </div>
      </div>
    </FormSection>
  )
}

export default FormOfferVenue
