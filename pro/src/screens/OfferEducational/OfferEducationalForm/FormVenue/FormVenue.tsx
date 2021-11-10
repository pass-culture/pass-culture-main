import React from 'react'

import { Select } from 'ui-kit'

import { OFFERER_LABEL, VENUE_LABEL } from '../../constants/labels'
import FormSection from '../FormSection'

import styles from './FormVenue.module.scss'

const FormVenue = (): JSX.Element => {
  return (
    <FormSection
      subtitle="Le lieu de rattachement permet d'associer vos coordonnées bancaires pour le remboursement pass Culture."
      title="Lieu de rattachement de votre offre"
    >
      <div className={styles.subsection}>
        <Select
          disabled
          label={OFFERER_LABEL}
          name='offerer'
          options={[]}
        />
      </div>
      <div className={styles.subsection}>
        <Select
          label={VENUE_LABEL}
          name='venueId'
          options={[]}
        />
      </div>
    </FormSection>
  )
}

export default FormVenue
