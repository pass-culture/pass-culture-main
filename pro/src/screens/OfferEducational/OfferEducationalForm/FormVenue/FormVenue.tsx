import React from 'react'

import Banner from 'components/layout/Banner/Banner'
import { IUserOfferer } from 'core/OfferEducational'
import FormLayout from 'new_components/FormLayout'
import { Select } from 'ui-kit'

import { OFFERER_LABEL, VENUE_LABEL } from '../../constants/labels'
import buildSelectOptions from '../../utils/buildSelectOptions'

interface IFormVenueProps {
  userOfferers: IUserOfferer[]
  venuesOptions: SelectOptions
  canCreateEducationalOffer: boolean | undefined
}

const FormVenue = ({
  userOfferers,
  venuesOptions,
  canCreateEducationalOffer,
}: IFormVenueProps): JSX.Element => {
  const offerersOptions = buildSelectOptions(
    userOfferers,
    'name',
    'id',
    'Selectionner une structure'
  )

  return (
    <FormLayout.Section
      description="Le lieu de rattachement permet d'associer vos coordonnées bancaires pour le remboursement pass Culture."
      title="Lieu de rattachement de votre offre"
    >
      <FormLayout.Row>
        <Select
          disabled={offerersOptions.length === 1}
          label={OFFERER_LABEL}
          name="offererId"
          options={offerersOptions}
        />
      </FormLayout.Row>
      {canCreateEducationalOffer === false && (
        <Banner href="#" linkTitle="Faire une demande de référencement">
          Pour proposer des offres à destination d’un groupe scolaire, vous
          devez être référencé auprès du ministère de l’Éducation Nationale et
          du ministère de la Culture.
        </Banner>
      )}
      {canCreateEducationalOffer === true && (
        <FormLayout.Row>
          <Select
            disabled={venuesOptions.length === 1 || !canCreateEducationalOffer}
            label={VENUE_LABEL}
            name="venueId"
            options={venuesOptions}
          />
        </FormLayout.Row>
      )}
    </FormLayout.Section>
  )
}

export default FormVenue
