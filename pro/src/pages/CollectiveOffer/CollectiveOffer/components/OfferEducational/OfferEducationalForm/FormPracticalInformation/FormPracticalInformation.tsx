import {
  GetEducationalOffererResponseModel,
  OfferAddressType,
} from 'apiClient/v1'
import { OfferEducationalFormValues } from 'commons/core/OfferEducational/types'
import { offerInterventionOptions } from 'commons/core/shared/interventionOptions'
import { SelectOption } from 'commons/custom_types/form'
import { selectInterventionAreas } from 'commons/utils/selectInterventionAreas'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { RadioButtonGroup } from 'design-system/RadioButtonGroup/RadioButtonGroup'
import { useCallback } from 'react'
import { useFormContext } from 'react-hook-form'
import { Select } from 'ui-kit/form/Select/Select'
import { TextArea } from 'ui-kit/form/TextArea/TextArea'
import { MultiSelect, Option } from 'ui-kit/MultiSelect/MultiSelect'
import { TipsBanner } from 'ui-kit/TipsBanner/TipsBanner'

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
  const { watch, setValue, getFieldState, register } =
    useFormContext<OfferEducationalFormValues>()

  const eventAddressValue = watch('eventAddress')

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
      required
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
      error={getFieldState('interventionArea').error?.message}
    />
  )

  const currentVenue =
    currentOfferer?.managedVenues.find(
      (venue) => venue.id === Number(eventAddressValue.venueId)
    ) || null

  const adressTypeRadios = [
    {
      label: EVENT_ADDRESS_VENUE_LABEL,
      value: OfferAddressType.OFFERER_VENUE,
      collapsed: (
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
      collapsed: (
        <FormLayout.Row
          sideComponent={
            <TipsBanner className={styles['info-box-children']}>
              La zone de mobilité permet d’indiquer aux enseignants sur ADAGE où
              vous pouvez vous déplacer en France.
            </TipsBanner>
          }
        >
          {MultiSelectComponent}
        </FormLayout.Row>
      ),
    },
    {
      label: EVENT_ADDRESS_OTHER_LABEL,
      value: OfferAddressType.OTHER,
      collapsed: (
        <FormLayout.Row
          sideComponent={
            <TipsBanner className={styles['info-box-children']}>
              La zone de mobilité permet d’indiquer aux enseignants sur ADAGE où
              vous pouvez vous déplacer en France.
            </TipsBanner>
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

  return (
    <FormLayout.Row>
      <RadioButtonGroup
        variant="detailed"
        checkedOption={watch('eventAddress.addressType')}
        onChange={(e) =>
          setValue(
            'eventAddress.addressType',
            e.target.value as OfferAddressType
          )
        }
        options={adressTypeRadios}
        label="Où se déroule votre offre ?"
        labelTag="h2"
        name="eventAddress.addressType"
        disabled={disableForm}
        required
      />
    </FormLayout.Row>
  )
}
