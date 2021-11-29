import { useFormikContext } from 'formik'
import React, { useEffect } from 'react'

import Banner from 'components/layout/Banner/Banner'
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
  canCreateEducationalOffer: boolean | undefined
}

const FormVenue = ({
  userOfferers,
  venuesOptions,
  canCreateEducationalOffer,
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
          options={
            values.offererId
              ? offerersOptions
              : [
                  ...offerersOptions,
                  { value: '', label: 'Sélectionnez une structure' },
                ]
          }
        />
      </FormLayout.Row>
      {canCreateEducationalOffer === false ? (
        <Banner href="#" linkTitle="Faire une demande de référencement">
          Pour proposer des offres à destination d’un groupe scolaire, vous
          devez être référencé auprès du ministère de l’Éducation Nationale et
          du ministère de la Culture.
        </Banner>
      ) : null}
      {canCreateEducationalOffer === true ? (
        <FormLayout.Row>
          <Select
            disabled={venuesOptions.length === 1 || !canCreateEducationalOffer}
            label={VENUE_LABEL}
            name="venueId"
            options={venuesOptions}
          />
        </FormLayout.Row>
      ) : null}
    </FormLayout.Section>
  )
}

export default FormVenue
