import { useFormikContext } from 'formik'
import { useCallback, useEffect, useState } from 'react'

import {
  GetEducationalOffererResponseModel,
  GetEducationalOffererVenueResponseModel,
  OfferAddressType,
} from 'apiClient/v1'
import { getDefaultEducationalValues } from 'commons/core/OfferEducational/constants'
import { OfferEducationalFormValues } from 'commons/core/OfferEducational/types'
import { offerInterventionOptions } from 'commons/core/shared/interventionOptions'
import { SelectOption } from 'commons/custom_types/form'
import { selectInterventionAreas } from 'commons/utils/selectInterventionAreas'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { Select } from 'ui-kit/form/Select/Select'
import { TextArea } from 'ui-kit/form/TextArea/TextArea'
import {
  RadioGroup,
  RadioGroupProps,
} from 'ui-kit/formV2/RadioGroup/RadioGroup'
import { InfoBox } from 'ui-kit/InfoBox/InfoBox'
import { MultiSelect, Option } from 'ui-kit/MultiSelect/MultiSelect'

import {
  EVENT_ADDRESS_OTHER_ADDRESS_LABEL,
  EVENT_ADDRESS_OTHER_LABEL,
  EVENT_ADDRESS_SCHOOL_LABEL,
  EVENT_ADDRESS_VENUE_LABEL,
  EVENT_ADDRESS_VENUE_SELECT_LABEL,
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
  const { values, setFieldValue, touched, errors, setFieldTouched } =
    useFormikContext<OfferEducationalFormValues>()

  const [currentVenue, setCurrentVenue] =
    useState<GetEducationalOffererVenueResponseModel | null>(null)

  const handleMultiSelectChange = useCallback(
    (
      selectedOption: Option[],
      addedOptions: Option[],
      removedOptions: Option[]
    ) => {
      const newSelectedOptions = selectInterventionAreas({
        selectedOption,
        addedOptions,
        removedOptions,
      })
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      setFieldValue('interventionArea', Array.from(newSelectedOptions))
    },
    [setFieldValue]
  )

  const MultiSelectComponent = (
    <MultiSelect
      label="Département(s)"
      name="interventionArea"
      buttonLabel="Département(s)"
      options={offerInterventionOptions}
      selectedOptions={offerInterventionOptions.filter((op) =>
        values.interventionArea.includes(op.id)
      )}
      defaultOptions={offerInterventionOptions.filter((option) =>
        values.interventionArea.includes(option.id)
      )}
      disabled={disableForm}
      hasSearch
      searchLabel="Rechercher"
      hasSelectAllOptions
      onSelectedOptionsChanged={handleMultiSelectChange}
      onBlur={() => setFieldTouched('interventionArea', true)}
      error={
        touched.interventionArea && errors.interventionArea
          ? String(errors.interventionArea)
          : undefined
      }
    />
  )

  const adressTypeRadios: RadioGroupProps['group'] = [
    {
      label: EVENT_ADDRESS_VENUE_LABEL,
      value: OfferAddressType.OFFERER_VENUE,
      sizing: 'fill',
      collapsed: (
        <FormLayout.Row>
          <Select
            disabled={venuesOptions.length === 1 || disableForm}
            label={EVENT_ADDRESS_VENUE_SELECT_LABEL}
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
      ),
    },
    {
      label: EVENT_ADDRESS_SCHOOL_LABEL,
      value: OfferAddressType.SCHOOL,
      sizing: 'fill',
      collapsed: (
        <FormLayout.Row
          sideComponent={
            <InfoBox className={styles['info-box-children']}>
              La zone de mobilité permet d’indiquer aux enseignants sur ADAGE où
              vous pouvez vous déplacer en France.
            </InfoBox>
          }
        >
          {MultiSelectComponent}
        </FormLayout.Row>
      ),
    },
    {
      label: EVENT_ADDRESS_OTHER_LABEL,
      value: OfferAddressType.OTHER,
      sizing: 'fill',
      collapsed: (
        <FormLayout.Row
          sideComponent={
            <InfoBox className={styles['info-box-children']}>
              La zone de mobilité permet d’indiquer aux enseignants sur ADAGE où
              vous pouvez vous déplacer en France.
            </InfoBox>
          }
        >
          {MultiSelectComponent}
          <TextArea
            label={EVENT_ADDRESS_OTHER_ADDRESS_LABEL}
            maxLength={200}
            name="eventAddress.otherAddress"
            disabled={disableForm}
            className={styles['event-other-address']}
          />
        </FormLayout.Row>
      ),
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
          getDefaultEducationalValues().eventAddress.venueId
        )
        setCurrentVenue(null)
      }

      if (
        values.eventAddress.addressType !== OfferAddressType.OTHER &&
        values.eventAddress.otherAddress
      ) {
        await setFieldValue(
          'eventAddress.otherAddress',
          getDefaultEducationalValues().eventAddress.otherAddress
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

  return (
    <FormLayout.Row>
      <RadioGroup
        variant="detailed"
        checkedOption={values.eventAddress.addressType}
        onChange={(e) =>
          setFieldValue('eventAddress.addressType', e.target.value)
        }
        group={adressTypeRadios}
        legend={
          <h2 className={styles['subtitle']}>Où se déroule votre offre ? *</h2>
        }
        name="eventAddress.addressType"
        disabled={disableForm}
      />
    </FormLayout.Row>
  )
}
