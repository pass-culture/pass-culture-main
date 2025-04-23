import { FieldInputProps, useFormikContext } from 'formik'
import { useId, useState } from 'react'

import {
  CollectiveLocationType,
  VenueListItemResponseModel,
} from 'apiClient/v1'
import { OfferEducationalFormValues } from 'commons/core/OfferEducational/types'
import {
  AddressSelect,
  AutocompleteItemProps,
} from 'components/Address/Address'
import { AddressManual } from 'components/AddressManual/AddressManual'
import { FormLayout } from 'components/FormLayout/FormLayout'
import fullBackIcon from 'icons/full-back.svg'
import fullNextIcon from 'icons/full-next.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { RadioGroup } from 'ui-kit/form/RadioGroup/RadioGroup'
import { RadioVariant } from 'ui-kit/form/shared/BaseRadio/BaseRadio'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'

import styles from '../OfferEducationalForm.module.scss'
export interface FormLocationProps {
  disableForm: boolean
  venues: VenueListItemResponseModel[]
}

const resetAddressFields = async (
  setFieldValue: (field: string, value: string | number | boolean) => void
) => {
  await Promise.all([
    setFieldValue('location.address.street', ''),
    setFieldValue('location.address.city', ''),
    setFieldValue('location.address.postalCode', ''),
    setFieldValue('location.address.longitude', ''),
    setFieldValue('location.address.latitude', ''),
    setFieldValue('location.address.banId', ''),
    setFieldValue('addressAutocomplete', ''),
    setFieldValue('search-addressAutocomplete', ''),
  ])
}

export const FormLocation = ({
  venues,
  disableForm,
}: FormLocationProps): JSX.Element => {
  const specificAddressId = useId()
  const { values, setFieldValue } =
    useFormikContext<OfferEducationalFormValues>()
  const [shouldShowManualAddressForm, setShouldShowManualAddressForm] =
    useState(false)

  const selectedVenue = venues.find(
    (v) => v.id.toString() === values.venueId.toString()
  )

  const toggleManualAddressForm = async () => {
    setShouldShowManualAddressForm(!shouldShowManualAddressForm)
    if (!shouldShowManualAddressForm) {
      await setFieldValue('location.address.isManualEdition', true)
      await resetAddressFields(setFieldValue)
    }
  }

  const handleAddressSelect = (
    setFieldValue: (field: string, value: string | number | boolean) => void,
    selectedItem?: AutocompleteItemProps,
    searchField?: FieldInputProps<string>
  ) => {
    const { address, postalCode, city, latitude, longitude } =
      selectedItem?.extraData || {}

    setFieldValue('location.address.street', address ?? '')
    if (searchField) {
      setFieldValue('addressAutocomplete', searchField.value)
    }
    setFieldValue('location.address.postalCode', postalCode ?? '')
    setFieldValue('location.address.city', city ?? '')
    setFieldValue('location.address.latitude', latitude ?? '')
    setFieldValue('location.address.longitude', longitude ?? '')
    setFieldValue('location.address.banId', selectedItem?.value ?? '')
    setFieldValue('location.address.isVenueAddress', false)
  }

  const handleAddressLocationChange = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const isSpecificAddress = event.target.value === 'SPECIFIC_ADDRESS'

    if (isSpecificAddress) {
      await setFieldValue('location.address.label', '')
      await resetAddressFields(setFieldValue)
    } else {
      // If here, the user chose to use the venue address
      const { address } = selectedVenue || {}
      await Promise.all([
        setFieldValue('location.address.banId', address?.banId),
        setFieldValue('location.address.isVenueAddress', true),
        setFieldValue('location.address.city', address?.city),
        setFieldValue('location.address.label', address?.label),
        setFieldValue('location.address.longitude', address?.longitude),
        setFieldValue('location.address.latitude', address?.latitude),
        setFieldValue('location.address.postalCode', address?.postalCode),
        setFieldValue('location.address.street', address?.street),
      ])
    }
  }

  const addressTypeRadios = [
    {
      label: <span id={specificAddressId}>À une adresse précise</span>,
      value: CollectiveLocationType.ADDRESS,
      childrenOnChecked: (
        <RadioGroup
          describedBy={specificAddressId}
          onChange={handleAddressLocationChange}
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
                    disabled={disableForm || shouldShowManualAddressForm}
                  />
                  <Button
                    variant={ButtonVariant.QUATERNARY}
                    icon={
                      shouldShowManualAddressForm ? fullBackIcon : fullNextIcon
                    }
                    onClick={toggleManualAddressForm}
                    disabled={disableForm}
                  >
                    {shouldShowManualAddressForm ? (
                      <>Revenir à la sélection automatique</>
                    ) : (
                      <>Vous ne trouvez pas votre adresse ?</>
                    )}
                  </Button>
                  {shouldShowManualAddressForm && (
                    <AddressManual
                      gpsCalloutMessage={
                        'Les coordonnées GPS sont des informations à ne pas négliger. Elles permettent aux enseignants de trouver votre offre sur ADAGE.'
                      }
                    />
                  )}
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
