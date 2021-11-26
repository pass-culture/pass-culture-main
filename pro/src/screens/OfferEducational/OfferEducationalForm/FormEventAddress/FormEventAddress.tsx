import { useFormikContext } from 'formik'
import React, { useEffect, useState } from 'react'

import Banner from 'components/layout/Banner/Banner'
import {
  INITIAL_EDUCATIONAL_FORM_VALUES,
  ADRESS_TYPE,
  IOfferEducationalFormValues,
  IUserOfferer,
  IUserVenue,
} from 'core/OfferEducational'
import FormLayout from 'new_components/FormLayout'
import { RadioButton, Select, TextArea } from 'ui-kit'

import {
  EVENT_ADDRESS_OFFERER_LABEL,
  EVENT_ADDRESS_OTHER_LABEL,
  EVENT_ADDRESS_SCHOOL_LABEL,
  EVENT_ADDRESS_OTHER_ADDRESS_LABEL,
  EVENT_ADDRESS_OFFERER_VENUE_SELECT_LABEL,
} from '../../constants/labels'

interface IFormEventAddressProps {
  venuesOptions: SelectOptions
  currentOfferer: IUserOfferer | null
}

const FormEventAddress = ({
  venuesOptions,
  currentOfferer,
}: IFormEventAddressProps): JSX.Element => {
  const { values, setFieldValue } =
    useFormikContext<IOfferEducationalFormValues>()
  const [currentVenue, setCurrentVenue] = useState<IUserVenue | null>(null)

  useEffect(() => {
    setFieldValue(
      'eventAddress.otherAddress',
      INITIAL_EDUCATIONAL_FORM_VALUES.eventAddress.otherAddress,
      false
    )

    setFieldValue(
      'eventAddress.venueId',
      INITIAL_EDUCATIONAL_FORM_VALUES.eventAddress.venueId,
      false
    )

    setCurrentVenue(null)
  }, [values.eventAddress.addressType, setFieldValue])

  useEffect(() => {
    if (
      values.eventAddress.addressType === ADRESS_TYPE.OFFERER_VENUE &&
      !!values.eventAddress.venueId
    ) {
      if (currentOfferer) {
        const selectedVenue = currentOfferer.managedVenues.find(
          venue => venue.id === values.eventAddress.venueId
        )
        return setCurrentVenue(selectedVenue ?? null)
      }

      return setCurrentVenue(null)
    }
  }, [currentOfferer, values.eventAddress])

  return (
    <FormLayout.Section
      description="Ces informations seront visibles par les établissements scolaires"
      title="Informations pratiques"
    >
      <FormLayout.SubSection title="Adresse où aura lieu l’événement">
        <FormLayout.Row>
          <RadioButton
            checked
            label={EVENT_ADDRESS_OFFERER_LABEL}
            name="eventAddress.addressType"
            value={ADRESS_TYPE.OFFERER_VENUE}
          />
          <RadioButton
            label={EVENT_ADDRESS_SCHOOL_LABEL}
            name="eventAddress.addressType"
            value={ADRESS_TYPE.SCHOOL}
          />
          <RadioButton
            label={EVENT_ADDRESS_OTHER_LABEL}
            name="eventAddress.addressType"
            value={ADRESS_TYPE.OTHER}
          />
        </FormLayout.Row>

        {values.eventAddress.addressType === ADRESS_TYPE.OFFERER_VENUE && (
          <>
            <FormLayout.Row>
              <Select
                label={EVENT_ADDRESS_OFFERER_VENUE_SELECT_LABEL}
                name="eventAddress.venueId"
                options={venuesOptions}
              />
            </FormLayout.Row>
            {currentVenue && (
              <Banner type="light">
                {currentVenue.name}
                <br />
                {currentVenue.address.street}, {currentVenue.address.postalCode}{' '}
                {currentVenue.address.city}
              </Banner>
            )}
          </>
        )}

        {values.eventAddress.addressType === ADRESS_TYPE.OTHER && (
          <FormLayout.Row>
            <TextArea
              label={EVENT_ADDRESS_OTHER_ADDRESS_LABEL}
              name="eventAddress.otherAddress"
            />
          </FormLayout.Row>
        )}
      </FormLayout.SubSection>
    </FormLayout.Section>
  )
}

export default FormEventAddress
