import React from 'react'

import { RadioButton } from 'ui-kit'

import {
  OFFER_VENUE_OFFERER_LABEL,
  OFFER_VENUE_OTHER_LABEL,
  OFFER_VENUE_SCHOOL_LABEL,
} from '../../constants/labels'
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
            label={OFFER_VENUE_OFFERER_LABEL}
            name='offerVenueId'
            value='offererVenue'
          />
          <RadioButton
            label={OFFER_VENUE_SCHOOL_LABEL}
            name='offerVenueId'
            value='school'
          />
          <RadioButton
            label={OFFER_VENUE_OTHER_LABEL}
            name='offerVenueId'
            value='other'
          />
        </div>
      </div>
    </FormSection>
  )
}

export default FormOfferVenue
