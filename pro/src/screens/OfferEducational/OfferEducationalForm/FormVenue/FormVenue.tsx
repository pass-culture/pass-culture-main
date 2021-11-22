import React from 'react'

import FormLayout from 'new_components/FormLayout'
import { Select } from 'ui-kit'

import { OFFERER_LABEL, VENUE_LABEL } from '../../constants/labels'

const FormVenue = (): JSX.Element => (
  <FormLayout.Section
    description="Le lieu de rattachement permet d'associer vos coordonnées bancaires pour le remboursement pass Culture."
    title="Lieu de rattachement de votre offre"
  >
    <FormLayout.Row>
      <Select disabled label={OFFERER_LABEL} name="offerer" options={[]} />
    </FormLayout.Row>
    <FormLayout.Row>
      <Select label={VENUE_LABEL} name="venueId" options={[]} />
    </FormLayout.Row>
  </FormLayout.Section>
)

export default FormVenue
