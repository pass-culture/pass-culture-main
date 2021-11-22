import React from 'react'

import FormLayout from 'new_components/FormLayout'
import { RadioButton } from 'ui-kit'

import {
  OFFER_VENUE_OFFERER_LABEL,
  OFFER_VENUE_OTHER_LABEL,
  OFFER_VENUE_SCHOOL_LABEL,
} from '../../constants/labels'

const FormOfferVenue = (): JSX.Element => {
  return (
    <FormLayout.Section
      description="Ces informations seront visibles par les établissements scolaires"
      title="Informations pratiques"
    >
      <FormLayout.SubSection title="Addresse où aura lieu l’événement">
        <FormLayout.Row>
          <RadioButton
            label={OFFER_VENUE_OFFERER_LABEL}
            name="offerVenueId"
            value="offererVenue"
          />
          <RadioButton
            label={OFFER_VENUE_SCHOOL_LABEL}
            name="offerVenueId"
            value="school"
          />
          <RadioButton
            label={OFFER_VENUE_OTHER_LABEL}
            name="offerVenueId"
            value="other"
          />
        </FormLayout.Row>
      </FormLayout.SubSection>
    </FormLayout.Section>
  )
}

export default FormOfferVenue
