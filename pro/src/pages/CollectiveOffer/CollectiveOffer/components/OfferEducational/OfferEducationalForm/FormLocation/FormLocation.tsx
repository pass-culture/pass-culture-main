import { FieldInputProps, useFormikContext } from 'formik'
import { useId } from 'react'

import {
  CollectiveLocationType,
  VenueListItemResponseModel,
} from 'apiClient/v1'
import { OfferEducationalFormValues } from 'commons/core/OfferEducational/types'
import {
  AddressSelect,
  AutocompleteItemProps,
} from 'components/Address/Address'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { RadioGroup } from 'ui-kit/form/RadioGroup/RadioGroup'
import { RadioVariant } from 'ui-kit/form/shared/BaseRadio/BaseRadio'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'

import styles from '../OfferEducationalForm.module.scss'

export interface FormLocationProps {
  disableForm: boolean
  venues: VenueListItemResponseModel[]
}

export const FormLocation = ({
  venues,
  disableForm,
}: FormLocationProps): JSX.Element => {
  const specificAddressId = useId()
  const { values, setFieldValue } =
    useFormikContext<OfferEducationalFormValues>()

  const selectedVenue = venues.find(
    (v) => v.id.toString() === values.venueId.toString()
  )

  const handleAddressSelect = (
    setFieldValue: any,
    selectedItem?: AutocompleteItemProps,
    searchField?: FieldInputProps<string>
  ) => {
    setFieldValue(
      'location.address.street',
      selectedItem?.extraData?.address ?? ''
    )
    if (searchField) {
      setFieldValue('addressAutocomplete', searchField.value)
    }
    setFieldValue(
      'location.address.postalCode',
      selectedItem?.extraData?.postalCode ?? ''
    )
    setFieldValue('location.address.city', selectedItem?.extraData?.city ?? '')
    setFieldValue(
      'location.address.latitude',
      selectedItem?.extraData?.latitude ?? ''
    )
    setFieldValue(
      'location.address.longitude',
      selectedItem?.extraData?.longitude ?? ''
    )
    setFieldValue('location.address.banId', selectedItem?.value ?? '')
    setFieldValue('location.address.isVenueAddress', false)
  }

  const onChangeAddressLocation = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const isSpecificAddress = event.target.value === 'SPECIFIC_ADDRESS'
    if (isSpecificAddress) {
      await setFieldValue('location.address.label', '')
      await setFieldValue('location.address.street', '')
      await setFieldValue('location.address.city', '')
      await setFieldValue('location.address.postalCode', '')
      await setFieldValue('location.address.longitude', '')
      await setFieldValue('location.address.latitude', '')
    }
  }

  const addressTypeRadios = [
    {
      label: <span id={specificAddressId}>À une adresse précise</span>,
      value: CollectiveLocationType.ADDRESS,
      childrenOnChecked: (
        <RadioGroup
          describedBy={specificAddressId}
          onChange={onChangeAddressLocation}
          variant={RadioVariant.BOX}
          disabled={disableForm}
          group={[
            {
              label: (
                <span>
                  {selectedVenue &&
                    `${selectedVenue.address?.label} - ${selectedVenue.address?.street}
                  ${selectedVenue.address?.postalCode} ${selectedVenue.address?.city}`}
                </span>
              ),
              value: selectedVenue?.address?.id_oa.toString() ?? '',
            },
            {
              label: 'Autre adresse',
              value: 'SPECIFIC_ADDRESS',
              childrenOnChecked: (
                <>
                  <TextInput
                    label="Intitulé de la localisation"
                    name="location.address.label"
                    isOptional
                    disabled={disableForm}
                  />
                  <AddressSelect
                    customHandleAddressSelect={handleAddressSelect}
                  />
                </>
              ),
            },
          ]}
          name={'location.id_oa'}
        />
      ),
    },
  ]

  return (
    <FormLayout.Row>
      <RadioGroup
        group={addressTypeRadios}
        legend={
          <h2 className={styles['subtitle']}>Où se déroule votre offre ?</h2>
        }
        name="location.locationType"
        variant={RadioVariant.BOX}
        disabled={disableForm}
      />
    </FormLayout.Row>
  )
}
