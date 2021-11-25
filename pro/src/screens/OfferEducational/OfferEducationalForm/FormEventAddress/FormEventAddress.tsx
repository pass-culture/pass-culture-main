import { useFormikContext } from 'formik'
import React, { useEffect } from 'react'

import {
  INITIAL_EDUCATIONAL_FORM_VALUES,
  IOfferEducationalFormValues,
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
  venuesOptions: { value: string; label: string }[]
}

const FormEventAddress = ({
  venuesOptions,
}: IFormEventAddressProps): JSX.Element => {
  const { values, setFieldValue } =
    useFormikContext<IOfferEducationalFormValues>()

  useEffect(() => {
    setFieldValue(
      'eventAddress.offererVenueId',
      INITIAL_EDUCATIONAL_FORM_VALUES.eventAddress.offererVenueId,
      false
    )
    setFieldValue(
      'eventAddress.otherAddress',
      INITIAL_EDUCATIONAL_FORM_VALUES.eventAddress.otherAddress,
      false
    )
  }, [values.eventAddress.addressType, setFieldValue])

  return (
    <FormLayout.Section
      description="Ces informations seront visibles par les établissements scolaires"
      title="Informations pratiques"
    >
      <FormLayout.SubSection title="Addresse où aura lieu l’événement">
        <FormLayout.Row>
          <RadioButton
            label={EVENT_ADDRESS_OFFERER_LABEL}
            name="eventAddress.addressType"
            value="offererVenue"
          />
          <RadioButton
            label={EVENT_ADDRESS_SCHOOL_LABEL}
            name="eventAddress.addressType"
            value="school"
          />
          <RadioButton
            label={EVENT_ADDRESS_OTHER_LABEL}
            name="eventAddress.addressType"
            value="other"
          />
        </FormLayout.Row>
        {values.eventAddress.addressType === 'offererVenue' && (
          <FormLayout.Row>
            <Select
              disabled={venuesOptions.length === 1}
              label={EVENT_ADDRESS_OFFERER_VENUE_SELECT_LABEL}
              name="eventAddress.offererVenueId"
              options={venuesOptions}
            />
          </FormLayout.Row>
        )}
        {values.eventAddress.addressType === 'other' && (
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
