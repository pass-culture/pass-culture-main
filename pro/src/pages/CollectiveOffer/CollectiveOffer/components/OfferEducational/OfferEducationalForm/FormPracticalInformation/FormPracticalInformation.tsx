import { useFormikContext } from 'formik'
import { useEffect, useState } from 'react'

import {
  GetEducationalOffererResponseModel,
  GetEducationalOffererVenueResponseModel,
  OfferAddressType,
} from 'apiClient/v1'
import { DEFAULT_EAC_FORM_VALUES } from 'commons/core/OfferEducational/constants'
import { OfferEducationalFormValues } from 'commons/core/OfferEducational/types'
import { offerInterventionOptions } from 'commons/core/shared/interventionOptions'
import { handleAllFranceDepartmentOptions } from 'commons/core/shared/utils/handleAllFranceDepartmentOptions'
import { SelectOption } from 'commons/custom_types/form'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { RadioGroup } from 'ui-kit/form/RadioGroup/RadioGroup'
import { Select } from 'ui-kit/form/Select/Select'
import { SelectAutocomplete } from 'ui-kit/form/SelectAutoComplete/SelectAutocomplete'
import { TextArea } from 'ui-kit/form/TextArea/TextArea'
import { InfoBox } from 'ui-kit/InfoBox/InfoBox'

import {
  EVENT_ADDRESS_OFFERER_LABEL,
  EVENT_ADDRESS_VENUE_LABEL,
  EVENT_ADDRESS_OFFERER_VENUE_SELECT_LABEL,
  EVENT_ADDRESS_VENUE_SELECT_LABEL,
  EVENT_ADDRESS_OTHER_ADDRESS_LABEL,
  EVENT_ADDRESS_OTHER_LABEL,
  EVENT_ADDRESS_SCHOOL_LABEL,
  INTERVENTION_AREA_LABEL,
} from '../../constants/labels'
import styles from '../OfferEducationalForm.module.scss'

export interface FormPracticalInformationProps {
  venuesOptions: SelectOption[]
  currentOfferer: GetEducationalOffererResponseModel | null
  disableForm: boolean
}

export const FormPracticalInformation = ({
  venuesOptions,
  currentOfferer,
  disableForm,
}: FormPracticalInformationProps): JSX.Element => {
  const { values, setFieldValue } =
    useFormikContext<OfferEducationalFormValues>()

  const [currentVenue, setCurrentVenue] =
    useState<GetEducationalOffererVenueResponseModel | null>(null)
  const [previousInterventionValues, setPreviousInterventionValues] = useState<
    string[] | null
  >(null)

  const isOfferAddressEnabled = useActiveFeature('WIP_ENABLE_OFFER_ADDRESS')

  const adressTypeRadios = [
    {
      label: isOfferAddressEnabled
        ? EVENT_ADDRESS_VENUE_LABEL
        : EVENT_ADDRESS_OFFERER_LABEL,
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

  useEffect(() => {
    async function setAddressField() {
      if (
        values.eventAddress.addressType !== OfferAddressType.OFFERER_VENUE &&
        values.eventAddress.venueId
      ) {
        await setFieldValue(
          'eventAddress.venueId',
          DEFAULT_EAC_FORM_VALUES.eventAddress.venueId
        )
        setCurrentVenue(null)
      }

      if (
        values.eventAddress.addressType !== OfferAddressType.OTHER &&
        values.eventAddress.otherAddress
      ) {
        await setFieldValue(
          'eventAddress.otherAddress',
          DEFAULT_EAC_FORM_VALUES.eventAddress.otherAddress
        )
      }
    }
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    setAddressField()
  }, [values.eventAddress, setFieldValue])

  useEffect(() => {
    async function setVenue() {
      if (
        values.eventAddress.addressType === OfferAddressType.OFFERER_VENUE &&
        values.eventAddress.venueId
      ) {
        if (currentOfferer) {
          const selectedVenue = currentOfferer.managedVenues.find(
            (venue) => venue.id === values.eventAddress.venueId
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
            (venue) => venue.id === Number(values.venueId)
          )
          if (selectedVenue) {
            await setFieldValue('eventAddress.venueId', values.venueId)
            return setCurrentVenue(selectedVenue)
          }
        }
        return setCurrentVenue(null)
      }

      if (!values.eventAddress.venueId) {
        return setCurrentVenue(null)
      }
    }
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    setVenue()
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
    <FormLayout.Section title="Où se déroule votre offre ?">
      <FormLayout.Row className={styles['address-radio-group']}>
        <RadioGroup
          group={adressTypeRadios}
          legend="Adresse où se déroulera l’évènement : *"
          name="eventAddress.addressType"
          disabled={disableForm}
        />
      </FormLayout.Row>

      {values.eventAddress.addressType === OfferAddressType.OFFERER_VENUE && (
        <FormLayout.Row>
          <Select
            disabled={venuesOptions.length === 1 || disableForm}
            label={
              isOfferAddressEnabled
                ? EVENT_ADDRESS_VENUE_SELECT_LABEL
                : EVENT_ADDRESS_OFFERER_VENUE_SELECT_LABEL
            }
            name="eventAddress.venueId"
            options={venuesOptions}
          />
          {currentVenue && (
            <div className={styles['educational-form-adress-banner']}>
              {currentVenue.name}
              <br />
              {currentVenue.street}, {currentVenue.postalCode}{' '}
              {currentVenue.city}
            </div>
          )}
        </FormLayout.Row>
      )}
      {values.eventAddress.addressType !== OfferAddressType.OFFERER_VENUE && (
        <FormLayout.Row
          sideComponent={
            <InfoBox>
              La zone de mobilité permet d’indiquer aux enseignants sur ADAGE où
              vous pouvez vous déplacer en France.
            </InfoBox>
          }
        >
          <SelectAutocomplete
            multi
            label={INTERVENTION_AREA_LABEL}
            name="interventionArea"
            hideTags
            options={offerInterventionOptions}
            className={styles.row}
            disabled={disableForm}
          />
        </FormLayout.Row>
      )}
      {values.eventAddress.addressType === OfferAddressType.OTHER && (
        <FormLayout.Row>
          <TextArea
            label={EVENT_ADDRESS_OTHER_ADDRESS_LABEL}
            maxLength={200}
            name="eventAddress.otherAddress"
            disabled={disableForm}
          />
        </FormLayout.Row>
      )}
    </FormLayout.Section>
  )
}
