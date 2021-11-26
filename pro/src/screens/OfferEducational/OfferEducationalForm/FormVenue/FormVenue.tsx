import { useFormikContext } from 'formik'
import React, { useEffect } from 'react'

import {
  INITIAL_EDUCATIONAL_FORM_VALUES,
  IOfferEducationalFormValues,
  IUserOfferer,
} from 'core/OfferEducational'
import FormLayout from 'new_components/FormLayout'
import { Select } from 'ui-kit'

import { OFFERER_LABEL, VENUE_LABEL } from '../../constants/labels'

interface IFormVenueProps {
  userOfferers: IUserOfferer[]
  venuesOptions: SelectOptions
}

const FormVenue = ({
  userOfferers,
  venuesOptions,
}: IFormVenueProps): JSX.Element => {
  const { values, setFieldValue } =
    useFormikContext<IOfferEducationalFormValues>()

  const offerersOptions = userOfferers.map(offerer => ({
    value: offerer.id,
    label: offerer.name,
  }))

  useEffect(() => {
    setFieldValue('venueId', INITIAL_EDUCATIONAL_FORM_VALUES.venueId, false)
    setFieldValue(
      'eventAddress.venueId',
      INITIAL_EDUCATIONAL_FORM_VALUES.eventAddress.venueId,
      false
    )
  }, [values.offererId, setFieldValue])

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
      <FormLayout.Row>
        <Select
          disabled={venuesOptions.length === 1}
          label={VENUE_LABEL}
          name="venueId"
          options={venuesOptions}
        />
      </FormLayout.Row>
    </FormLayout.Section>
  )
}

export default FormVenue
