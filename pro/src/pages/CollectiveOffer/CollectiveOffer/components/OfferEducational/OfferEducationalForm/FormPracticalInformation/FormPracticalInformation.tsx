import { useCallback, useEffect, useState } from 'react'
import { useFormContext } from 'react-hook-form'

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
import { RadioVariant } from 'ui-kit/form/shared/BaseRadio/BaseRadio'
import { RadioGroup } from 'ui-kit/formV2/RadioGroup/RadioGroup'
import { Select } from 'ui-kit/formV2/Select/Select'
import { TextArea } from 'ui-kit/formV2/TextArea/TextArea'
import { InfoBox } from 'ui-kit/InfoBox/InfoBox'
import { MultiSelect, Option } from 'ui-kit/MultiSelect/MultiSelect'

import {
  EVENT_ADDRESS_VENUE_LABEL,
  EVENT_ADDRESS_VENUE_SELECT_LABEL,
  EVENT_ADDRESS_OTHER_ADDRESS_LABEL,
  EVENT_ADDRESS_OTHER_LABEL,
  EVENT_ADDRESS_SCHOOL_LABEL,
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
  const { watch, setValue, getFieldState, register } =
    useFormContext<OfferEducationalFormValues>()

  const eventAddressValue = watch('eventAddress')
  const venueIdValue = watch('venueId')

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

      setValue('interventionArea', Array.from(newSelectedOptions))
    },
    [setValue]
  )

  const MultiSelectComponent = (
    <MultiSelect
      label="Département(s)"
      name="interventionArea"
      buttonLabel="Département(s)"
      options={offerInterventionOptions}
      selectedOptions={offerInterventionOptions.filter((op) =>
        watch('interventionArea')?.includes(op.id)
      )}
      defaultOptions={offerInterventionOptions.filter((option) =>
        watch('interventionArea')?.includes(option.id)
      )}
      disabled={disableForm}
      hasSearch
      searchLabel="Rechercher"
      hasSelectAllOptions
      onSelectedOptionsChanged={handleMultiSelectChange}
      onBlur={() =>
        setValue('interventionArea', watch('interventionArea'), {
          shouldTouch: true,
        })
      }
      error={
        getFieldState('interventionArea').isTouched
          ? getFieldState('interventionArea').error?.message
          : undefined
      }
    />
  )

  const adressTypeRadios = [
    {
      label: EVENT_ADDRESS_VENUE_LABEL,
      value: OfferAddressType.OFFERER_VENUE,
      childrenOnChecked: (
        <FormLayout.Row>
          <Select
            disabled={venuesOptions.length === 1 || disableForm}
            label={EVENT_ADDRESS_VENUE_SELECT_LABEL}
            {...register('eventAddress.venueId')}
            options={venuesOptions}
            required
            error={getFieldState('eventAddress.venueId').error?.message}
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
      childrenOnChecked: (
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
      childrenOnChecked: (
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
            required
            {...register('eventAddress.otherAddress')}
            label={EVENT_ADDRESS_OTHER_ADDRESS_LABEL}
            maxLength={200}
            error={getFieldState('eventAddress.otherAddress').error?.message}
            disabled={disableForm}
            className={styles['event-other-address']}
          />
        </FormLayout.Row>
      ),
    },
  ]

  useEffect(() => {
    function setAddressField() {
      if (
        eventAddressValue?.addressType !== OfferAddressType.OFFERER_VENUE &&
        eventAddressValue?.venueId
      ) {
        setValue(
          'eventAddress.venueId',
          getDefaultEducationalValues().eventAddress?.venueId || null
        )
        setCurrentVenue(null)
      }

      if (
        eventAddressValue?.addressType !== OfferAddressType.OTHER &&
        eventAddressValue?.otherAddress
      ) {
        setValue(
          'eventAddress.otherAddress',
          getDefaultEducationalValues().eventAddress?.otherAddress || ''
        )
      }
    }
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    setAddressField()
  }, [eventAddressValue])

  useEffect(() => {
    function setVenue() {
      if (
        eventAddressValue?.addressType === OfferAddressType.OFFERER_VENUE &&
        eventAddressValue.venueId
      ) {
        if (currentOfferer) {
          const selectedVenue = currentOfferer.managedVenues.find(
            (venue) => venue.id === eventAddressValue.venueId
          )
          return setCurrentVenue(selectedVenue ?? null)
        }
        return setCurrentVenue(null)
      }

      if (
        eventAddressValue?.addressType === OfferAddressType.OFFERER_VENUE &&
        !eventAddressValue.venueId &&
        watch('venueId')
      ) {
        if (currentOfferer) {
          const selectedVenue = currentOfferer.managedVenues.find(
            (venue) => venue.id === Number(venueIdValue)
          )
          if (selectedVenue) {
            setValue('eventAddress.venueId', Number(venueIdValue))
            return setCurrentVenue(selectedVenue)
          }
        }
        return setCurrentVenue(null)
      }

      if (!eventAddressValue?.venueId) {
        return setCurrentVenue(null)
      }
    }
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    setVenue()
  }, [currentOfferer, eventAddressValue])

  return (
    <FormLayout.Row>
      <RadioGroup
        group={adressTypeRadios}
        legend={
          <h2 className={styles['subtitle']}>Où se déroule votre offre ? *</h2>
        }
        name="eventAddress.addressType"
        checkedOption={watch('eventAddress.addressType')}
        onChange={(e) =>
          setValue(
            'eventAddress.addressType',
            e.target.value as OfferAddressType
          )
        }
        variant={RadioVariant.BOX}
        disabled={disableForm}
      />
    </FormLayout.Row>
  )
}
