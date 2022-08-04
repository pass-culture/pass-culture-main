import { useFormikContext } from 'formik'
import React from 'react'

import { GetEducationalOffererResponseModel } from 'apiClient/v1'
import { IOfferEducationalFormValues } from 'core/OfferEducational'
import FormLayout from 'new_components/FormLayout'
import { Banner, Select } from 'ui-kit'

import { OFFERER_LABEL, VENUE_LABEL } from '../../constants/labels'

interface IFormVenueProps {
  userOfferers: GetEducationalOffererResponseModel[]
  venuesOptions: SelectOptions
  isEligible: boolean | undefined
  disableForm: boolean
}

const FormVenue = ({
  userOfferers,
  venuesOptions,
  isEligible,
  disableForm,
}: IFormVenueProps): JSX.Element => {
  let offerersOptions = userOfferers.map(item => ({
    value: item['id'] as string,
    label: item['name'] as string,
  }))
  if (offerersOptions.length > 1) {
    offerersOptions = [
      { value: '', label: 'Selectionner une structure' },
      ...offerersOptions,
    ]
  }

  const { values } = useFormikContext<IOfferEducationalFormValues>()

  return (
    <FormLayout.Section
      description="Le lieu de rattachement permet d'associer vos coordonnées bancaires pour le remboursement pass Culture."
      title="Lieu de rattachement de votre offre"
    >
      <FormLayout.Row>
        <Select
          disabled={offerersOptions.length === 1 || disableForm}
          label={OFFERER_LABEL}
          name="offererId"
          options={offerersOptions}
        />
      </FormLayout.Row>
      {isEligible === false && offerersOptions.length !== 0 && (
        <Banner
          href="https://passculture.typeform.com/to/VtKospEg"
          linkTitle="Faire une demande de référencement"
        >
          Pour proposer des offres à destination d’un groupe, vous devez être
          référencé auprès du ministère de l’Éducation Nationale et du ministère
          de la Culture.
        </Banner>
      )}

      {venuesOptions.length === 0 && offerersOptions.length !== 0 && (
        <Banner
          href={`/structures/${values.offererId}/lieux/creation`}
          linkTitle="Renseigner un lieu"
        >
          Pour proposer des offres à destination d’un groupe, vous devez
          renseigner un lieu pour pouvoir être remboursé.
        </Banner>
      )}
      {offerersOptions.length === 0 && (
        <Banner>
          Vous ne pouvez pas créer d’offre collective tant que votre structure
          n’est pas validée.
        </Banner>
      )}
      {isEligible === true && venuesOptions.length > 0 && (
        <FormLayout.Row>
          <Select
            disabled={venuesOptions.length === 1 || !isEligible || disableForm}
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
