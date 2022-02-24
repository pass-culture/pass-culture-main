import { useFormikContext } from 'formik'
import React, { useEffect, useState } from 'react'

import {
  DEFAULT_EAC_FORM_VALUES,
  ADRESS_TYPE,
  IOfferEducationalFormValues,
  IUserOfferer,
  IUserVenue,
} from 'core/OfferEducational'
import FormLayout from 'new_components/FormLayout'
import { RadioGroup, Select, TextArea } from 'ui-kit'
import { Banner } from 'ui-kit'

import {
  EVENT_ADDRESS_OFFERER_LABEL,
  EVENT_ADDRESS_OTHER_LABEL,
  EVENT_ADDRESS_SCHOOL_LABEL,
  EVENT_ADDRESS_OTHER_ADDRESS_LABEL,
  EVENT_ADDRESS_OFFERER_VENUE_SELECT_LABEL,
} from '../../constants/labels'
import styles from '../OfferEducationalForm.module.scss'

interface IFormEventAddressProps {
  venuesOptions: SelectOptions
  currentOfferer: IUserOfferer | null
}

const adressTypeRadios = [
  {
    label: EVENT_ADDRESS_OFFERER_LABEL,
    value: ADRESS_TYPE.OFFERER_VENUE,
  },
  {
    label: EVENT_ADDRESS_SCHOOL_LABEL,
    value: ADRESS_TYPE.SCHOOL,
  },
  {
    label: EVENT_ADDRESS_OTHER_LABEL,
    value: ADRESS_TYPE.OTHER,
  },
]

const FormEventAddress = ({
  venuesOptions,
  currentOfferer,
}: IFormEventAddressProps): JSX.Element => {
  const { values, setFieldValue } =
    useFormikContext<IOfferEducationalFormValues>()
  const [currentVenue, setCurrentVenue] = useState<IUserVenue | null>(null)

  useEffect(() => {
    if (
      values.eventAddress.addressType !== ADRESS_TYPE.OFFERER_VENUE &&
      values.eventAddress.venueId
    ) {
      setFieldValue(
        'eventAddress.venueId',
        DEFAULT_EAC_FORM_VALUES.eventAddress.venueId
      )
      setCurrentVenue(null)
    }

    if (
      values.eventAddress.addressType !== ADRESS_TYPE.OTHER &&
      values.eventAddress.otherAddress
    ) {
      setFieldValue(
        'eventAddress.otherAddress',
        DEFAULT_EAC_FORM_VALUES.eventAddress.otherAddress
      )
    }
  }, [values.eventAddress, setFieldValue])

  useEffect(() => {
    if (
      values.eventAddress.addressType === ADRESS_TYPE.OFFERER_VENUE &&
      values.eventAddress.venueId
    ) {
      if (currentOfferer) {
        const selectedVenue = currentOfferer.managedVenues.find(
          venue => venue.id === values.eventAddress.venueId
        )
        return setCurrentVenue(selectedVenue ?? null)
      }
      return setCurrentVenue(null)
    }

    if (!values.eventAddress.venueId) {
      return setCurrentVenue(null)
    }
  }, [currentOfferer, values.eventAddress])

  return (
    <FormLayout.Section
      description="Ces informations sont visibles par les enseignants et les chefs d’établissement."
      title="Informations pratiques"
    >
      <FormLayout.Row>
        <RadioGroup
          group={adressTypeRadios}
          legend="Adresse où se déroulera l’événement :"
          name="eventAddress.addressType"
        />
      </FormLayout.Row>

      {values.eventAddress.addressType === ADRESS_TYPE.OFFERER_VENUE && (
        <FormLayout.Row>
          <Select
            disabled={venuesOptions.length === 1}
            label={EVENT_ADDRESS_OFFERER_VENUE_SELECT_LABEL}
            name="eventAddress.venueId"
            options={venuesOptions}
          />
          {currentVenue && (
            <Banner
              className={styles['educational-form-adress-banner']}
              type="light"
            >
              {currentVenue.name}
              <br />
              {currentVenue.address.street}, {currentVenue.address.postalCode}{' '}
              {currentVenue.address.city}
            </Banner>
          )}
        </FormLayout.Row>
      )}

      {values.eventAddress.addressType === ADRESS_TYPE.OTHER && (
        <FormLayout.Row>
          <TextArea
            countCharacters
            label={EVENT_ADDRESS_OTHER_ADDRESS_LABEL}
            maxLength={200}
            name="eventAddress.otherAddress"
          />
        </FormLayout.Row>
      )}
    </FormLayout.Section>
  )
}

export default FormEventAddress
