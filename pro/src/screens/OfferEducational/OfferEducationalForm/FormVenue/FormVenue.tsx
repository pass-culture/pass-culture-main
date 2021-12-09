import { useFormikContext } from 'formik'
import React from 'react'

import Banner from 'components/layout/Banner/Banner'
import {
  IOfferEducationalFormValues,
  IUserOfferer,
} from 'core/OfferEducational'
import FormLayout from 'new_components/FormLayout'
import { Select } from 'ui-kit'

import { OFFERER_LABEL, VENUE_LABEL } from '../../constants/labels'
import buildSelectOptions from '../../utils/buildSelectOptions'

interface IFormVenueProps {
  userOfferers: IUserOfferer[]
  venuesOptions: SelectOptions
  isEligible: boolean | undefined
}

const FormVenue = ({
  userOfferers,
  venuesOptions,
  isEligible,
}: IFormVenueProps): JSX.Element => {
  const offerersOptions = buildSelectOptions(
    userOfferers,
    'name',
    'id',
    'Selectionner une structure'
  )

  const { values } = useFormikContext<IOfferEducationalFormValues>()

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
      {isEligible === false && (
        <Banner href="#" linkTitle="Faire une demande de référencement">
          Pour proposer des offres à destination d’un groupe scolaire, vous
          devez être référencé auprès du ministère de l’Éducation Nationale et
          du ministère de la Culture.
        </Banner>
      )}
      {venuesOptions.length === 0 && (
        <Banner
          href={`/structures/${values.offererId}/lieux/creation`}
          linkTitle="Renseigner un lieu"
        >
          Pour proposer des offres à destination d’un groupe scolaire, vous
          devez renseigner un lieu pour pouvoir être remboursé.
        </Banner>
      )}
      {isEligible === true && venuesOptions.length > 0 && (
        <FormLayout.Row>
          <Select
            disabled={venuesOptions.length === 1 || !isEligible}
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
