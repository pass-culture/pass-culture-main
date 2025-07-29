import React, { useState } from 'react'
import { useFormContext } from 'react-hook-form'

import { VenueListItemResponseModel } from 'apiClient/v1'
import { AddressFormValues } from 'commons/core/shared/types'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { RadioButtonGroup } from 'design-system/RadioButtonGroup/RadioButtonGroup'
import fullBackIcon from 'icons/full-back.svg'
import fullNextIcon from 'icons/full-next.svg'
import { OFFER_LOCATION } from 'pages/IndividualOffer/commons/constants'
import { computeAddressDisplayName } from 'repository/venuesService'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { AddressManual } from 'ui-kit/form/AddressManual/AddressManual'
import { AddressSelect } from 'ui-kit/form/AddressSelect/AddressSelect'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'

import { UsefulInformationFormValues } from '../../commons/types'

import styles from './OfferLocation.module.scss'

export interface OfferLocationProps {
  venue: VenueListItemResponseModel | undefined
  readOnlyFields: string[]
}

export const OfferLocation = ({
  venue,
  readOnlyFields,
}: OfferLocationProps): JSX.Element => {
  const {
    register,
    watch,
    setValue,
    formState: { errors },
  } = useFormContext<UsefulInformationFormValues>()
  const offerLocation = watch('offerLocation')
  const manuallySetAddress = watch('manuallySetAddress')

  const [showOtherAddress, setShowOtherAddress] = useState(
    offerLocation === OFFER_LOCATION.OTHER_ADDRESS
  )

  const resetAddressFields = () => {
    const fieldNames: (keyof AddressFormValues)[] = [
      'street',
      'postalCode',
      'city',
      'latitude',
      'longitude',
      'coords',
      'banId',
      'inseeCode',
      'search-addressAutocomplete',
      'addressAutocomplete',
    ]

    fieldNames.forEach((fieldName) => {
      setValue(fieldName, '')
    })
  }

  const onChangeOfferLocation = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const isVenueAddress = event.target.value !== OFFER_LOCATION.OTHER_ADDRESS
    setShowOtherAddress(!isVenueAddress)
    setValue('manuallySetAddress', false)

    if (isVenueAddress) {
      // If here, the user chose to use the venue address so
      // we reset the form fields with the related address values.

      // Avoid crashes if the venue doesn't have an OA, but this shouldn't technically happens
      if (!venue?.address) {
        return
      }

      setValue('inseeCode', venue.address.inseeCode ?? '')
      setValue('banId', venue.address.banId ?? '')
      setValue('city', venue.address.city)
      setValue('latitude', venue.address.latitude.toString())
      setValue('longitude', venue.address.longitude.toString())
      setValue(
        'coords',
        `${venue.address.latitude}, ${venue.address.longitude}`
      )
      setValue('postalCode', venue.address.postalCode)
      setValue('street', venue.address.street ?? '')
      setValue('locationLabel', venue.address.label ?? '')
      setValue('offerLocation', venue.address.id_oa.toString())
    } else {
      resetAddressFields()
      setValue('locationLabel', '')
      setValue('offerLocation', OFFER_LOCATION.OTHER_ADDRESS)
    }
  }

  const toggleManuallySetAddress = () => {
    setValue('manuallySetAddress', !manuallySetAddress)
  }

  const venueAddress = venue?.address
    ? computeAddressDisplayName(venue.address, false)
    : ''
  const venueFullText = `${venue?.publicName || venue?.name} – ${venueAddress}`

  return (
    <>
      <RadioButtonGroup
        label="Il s’agit de l’adresse à laquelle les jeunes devront se présenter."
        name="offerLocation"
        variant="detailed"
        options={[
          {
            label: venueFullText,
            value: venue?.address?.id_oa.toString() ?? '',
          },
          {
            label: 'À une autre adresse',
            value: OFFER_LOCATION.OTHER_ADDRESS,
          },
        ]}
        checkedOption={offerLocation}
        onChange={onChangeOfferLocation}
        disabled={readOnlyFields.includes('offerLocation')}
      />
      {showOtherAddress && (
        <div className={styles['other-address-wrapper']}>
          <FormLayout.Row className={styles['location-row']}>
            <TextInput
              {...register('locationLabel')}
              label="Intitulé de la localisation"
              disabled={readOnlyFields.includes('locationLabel')}
            />
          </FormLayout.Row>
          <FormLayout.Row>
            <AddressSelect
              {...register('addressAutocomplete')}
              label="Adresse postale"
              // TODO (igabriele, 2025-07-25): Simplify this logic.
              disabled={
                manuallySetAddress ||
                readOnlyFields.includes('addressAutocomplete')
              }
              className={styles['location-field']}
              error={errors.addressAutocomplete?.message}
              onAddressChosen={(addressData) => {
                setValue('manuallySetAddress', false)
                setValue('street', addressData.address)
                setValue('postalCode', addressData.postalCode)
                setValue('city', addressData.city)
                setValue('latitude', String(addressData.latitude))
                setValue('longitude', String(addressData.longitude))
                setValue('banId', addressData.id)
                setValue('inseeCode', addressData.inseeCode)
              }}
            />
          </FormLayout.Row>
          <FormLayout.Row>
            <Button
              variant={ButtonVariant.QUATERNARY}
              icon={manuallySetAddress ? fullBackIcon : fullNextIcon}
              onClick={toggleManuallySetAddress}
              disabled={readOnlyFields.includes('manuallySetAddress')}
            >
              {manuallySetAddress ? (
                <>Revenir à la sélection automatique</>
              ) : (
                <>Vous ne trouvez pas votre adresse ?</>
              )}
            </Button>
          </FormLayout.Row>
          {manuallySetAddress && (
            <AddressManual readOnlyFields={readOnlyFields} />
          )}
        </div>
      )}
    </>
  )
}
