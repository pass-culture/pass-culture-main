import { useFormikContext } from 'formik'
import React, { useEffect, useState } from 'react'

import {
  GetEducationalOffererResponseModel,
  GetEducationalOffererVenueResponseModel,
  OfferAddressType,
} from 'apiClient/v1'
import FormLayout from 'components/FormLayout'
import {
  DEFAULT_EAC_FORM_VALUES,
  IOfferEducationalFormValues,
  MAX_DETAILS_LENGTH,
} from 'core/OfferEducational'
import { handleAllFranceDepartmentOptions } from 'core/shared'
import { offerInterventionOptions } from 'core/shared/interventionOptions'
import {
  RadioGroup,
  Select,
  TextArea,
  Banner,
  MultiSelectAutocomplete,
  InfoBox,
} from 'ui-kit'

import {
  EVENT_ADDRESS_OFFERER_LABEL,
  EVENT_ADDRESS_OFFERER_VENUE_SELECT_LABEL,
  EVENT_ADDRESS_OTHER_ADDRESS_LABEL,
  EVENT_ADDRESS_OTHER_LABEL,
  EVENT_ADDRESS_SCHOOL_LABEL,
  INTERVENTION_AREA_LABEL,
  INTERVENTION_AREA_PLURAL_LABEL,
  PRICE_INFORMATION,
} from '../../constants/labels'
import styles from '../OfferEducationalForm.module.scss'

export interface IFormPracticalInformationProps {
  venuesOptions: SelectOptions
  currentOfferer: GetEducationalOffererResponseModel | null
  disableForm: boolean
  isTemplate: boolean
}

const adressTypeRadios = [
  {
    label: EVENT_ADDRESS_OFFERER_LABEL,
    value: OfferAddressType.OFFERER_VENUE,
  },
  {
    label: EVENT_ADDRESS_SCHOOL_LABEL,
    value: OfferAddressType.SCHOOL,
  },
  {
    label: EVENT_ADDRESS_OTHER_LABEL,
    value: OfferAddressType.OTHER,
  },
]

const FormPracticalInformation = ({
  venuesOptions,
  currentOfferer,
  disableForm,
  isTemplate,
}: IFormPracticalInformationProps): JSX.Element => {
  const { values, setFieldValue } =
    useFormikContext<IOfferEducationalFormValues>()

  const [currentVenue, setCurrentVenue] =
    useState<GetEducationalOffererVenueResponseModel | null>(null)
  const [previousInterventionValues, setPreviousInterventionValues] = useState<
    string[] | null
  >(null)

  useEffect(() => {
    if (
      values.eventAddress.addressType !== OfferAddressType.OFFERER_VENUE &&
      values.eventAddress.venueId
    ) {
      setFieldValue(
        'eventAddress.venueId',
        DEFAULT_EAC_FORM_VALUES.eventAddress.venueId
      )
      setCurrentVenue(null)
    }

    if (
      values.eventAddress.addressType !== OfferAddressType.OTHER &&
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
      values.eventAddress.addressType === OfferAddressType.OFFERER_VENUE &&
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

    if (
      values.eventAddress.addressType === OfferAddressType.OFFERER_VENUE &&
      !values.eventAddress.venueId &&
      values.venueId
    ) {
      if (currentOfferer) {
        const selectedVenue = currentOfferer.managedVenues.find(
          venue => venue.id === values.venueId
        )
        if (selectedVenue) {
          setFieldValue('eventAddress.venueId', values.venueId)
          return setCurrentVenue(selectedVenue)
        }
      }
      return setCurrentVenue(null)
    }

    if (!values.eventAddress.venueId) {
      return setCurrentVenue(null)
    }
  }, [currentOfferer, values.eventAddress])

  useEffect(() => {
    handleAllFranceDepartmentOptions(
      values.interventionArea,
      previousInterventionValues,
      (value: string[]) => setFieldValue('interventionArea', value)
    )

    setPreviousInterventionValues(values.interventionArea)
  }, [values.interventionArea])

  return (
    <FormLayout.Section
      description="Ces informations sont visibles par les enseignants et les chefs d’établissement."
      title="Informations pratiques"
    >
      <FormLayout.Row>
        <RadioGroup
          group={adressTypeRadios}
          legend="Adresse où se déroulera l’évènement :"
          name="eventAddress.addressType"
          disabled={disableForm}
        />
      </FormLayout.Row>

      {values.eventAddress.addressType === OfferAddressType.OFFERER_VENUE && (
        <FormLayout.Row>
          <Select
            disabled={venuesOptions.length === 1 || disableForm}
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
              {currentVenue.address}, {currentVenue.postalCode}{' '}
              {currentVenue.city}
            </Banner>
          )}
        </FormLayout.Row>
      )}

      {values.eventAddress.addressType !== OfferAddressType.OFFERER_VENUE && (
        <FormLayout.Row
          sideComponent={
            <InfoBox
              type="info"
              text="La zone de mobilité permet d’indiquer aux enseignants sur Adage où vous pouvez vous déplacer en France."
            />
          }
        >
          <MultiSelectAutocomplete
            hideTags
            options={offerInterventionOptions}
            name="interventionArea"
            pluralLabel={INTERVENTION_AREA_PLURAL_LABEL}
            label={INTERVENTION_AREA_LABEL}
            className={styles.row}
            disabled={disableForm}
          />
        </FormLayout.Row>
      )}

      {values.eventAddress.addressType === OfferAddressType.OTHER && (
        <FormLayout.Row>
          <TextArea
            countCharacters
            label={EVENT_ADDRESS_OTHER_ADDRESS_LABEL}
            maxLength={200}
            name="eventAddress.otherAddress"
            disabled={disableForm}
          />
        </FormLayout.Row>
      )}

      {isTemplate && (
        <FormLayout.Row>
          <TextArea
            className={styles['price-details']}
            countCharacters
            disabled={disableForm}
            isOptional
            label={PRICE_INFORMATION}
            maxLength={MAX_DETAILS_LENGTH}
            name="priceDetail"
            placeholder="Par exemple : tarif par élève ou par groupe scolaire, politique tarifaire REP/REP+ et accompagnateurs... "
          />
        </FormLayout.Row>
      )}
    </FormLayout.Section>
  )
}

export default FormPracticalInformation
